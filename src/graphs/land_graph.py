import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_land_all(land_df, theme):
    land_df.sort_values('created_date', inplace=True)

    fig = px.bar(land_df,
                 x='created_date',
                 y='received_amount',
                 color='resource_symbol',
                 barmode='group',
                 title='Amount harvest',
                 labels={
                     "received_amount": "Received amount (log)",
                     "created_date": "Harvest date",
                     "resource_symbol": "Resource"
                 })
    fig.update_layout(
        template=theme,
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            title="amount (log)",
            type="log",
            exponentformat="none",
            dtick=1,
        ),
    )
    return fig


def plot_land_pools(df, theme):
    df.sort_values('date', inplace=True)

    tokens = df['token'].unique()
    figures = {}

    color_value = '#1f77b4'
    color_resource = '#ff7f0e'
    color_dec = '#2ca02c'

    for token in tokens:
        df_token = df[df['token'] == token]

        # Calculate max values for y-axis ranges
        max_value = df_token['value'].max() * 1.1
        max_my_resource_quantity = df_token['my_resource_quantity'].max() * 1.1
        max_my_dec_quantity = df_token['my_dec_quantity'].max() * 1.1

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=df_token['date'],
                       y=df_token['value'],
                       mode='lines+markers',
                       line=dict(color=color_value),
                       marker=dict(color=color_value),
                       name=f'{token} Value',
                       yaxis='y1')
        )
        fig.add_trace(
            go.Scatter(x=df_token['date'],
                       y=df_token['my_resource_quantity'],
                       mode='lines+markers',
                       line=dict(color=color_resource),
                       marker=dict(color=color_resource),
                       name=f'{token} Resource Quantity',
                       yaxis='y2')
        )
        fig.add_trace(
            go.Scatter(x=df_token['date'],
                       y=df_token['my_dec_quantity'],
                       mode='lines+markers',
                       line=dict(color=color_dec),
                       marker=dict(color=color_dec),
                       name=f'{token} DEC Quantity',
                       yaxis='y3')
        )

        fig.update_layout(
            template=theme,
            title=f'Pool Information for {token}',
            xaxis=dict(title='Date'),
            yaxis=dict(
                title='Value ($)',
                titlefont=dict(color=color_value),
                tickfont=dict(color=color_value),
                side='right',
                range=[0, max_value],
                showgrid=True,
                zeroline=True
            ),
            yaxis2=dict(
                title='Resource Quantity',
                titlefont=dict(color=color_resource),
                tickfont=dict(color=color_resource),
                anchor="free",
                overlaying="y",
                side="left",
                position=0,
                range=[0, max_my_resource_quantity],
                showgrid=False,
                zeroline=True
            ),
            yaxis3=dict(
                title='DEC Quantity',
                titlefont=dict(color=color_dec),
                tickfont=dict(color=color_dec),
                anchor="free",
                overlaying="y",
                side="left",
                position=0.1,
                range=[0, max_my_dec_quantity],
                showgrid=False,
                zeroline=True
            ),
            legend=dict(x=1.1, y=1, traceorder='grouped'),
            hovermode='x unified'
        )

        figures[token] = fig

    return figures  # Return a dictionary of figures


def plot_cumsum(land_df, theme):
    land_df = land_df.pivot(index='created_date', columns='resource_symbol',
                            values=['received_amount', 'grain_eaten', 'grain_rewards_eaten', 'resource_amount',
                                    'tax_amount'])
    land_df = land_df.fillna(0)

    result_df = pd.DataFrame()

    if ('received_amount', 'GRAIN') in land_df.columns:
        land_df['GRAIN_earned'] = (land_df[('received_amount', 'GRAIN')]
                                   + land_df[('grain_rewards_eaten', 'GRAIN')]
                                   - land_df[('grain_eaten', 'GRAIN')])
        if ('received_amount', 'SPS') in land_df.columns:
            land_df['GRAIN_earned'] = land_df['GRAIN_earned'] - land_df[('grain_eaten', 'SPS')]
        if ('received_amount', 'RESEARCH') in land_df.columns:
            land_df['GRAIN_earned'] = land_df['GRAIN_earned'] - land_df[('grain_eaten', 'RESEARCH')]

        result_df['GRAIN'] = land_df['GRAIN_earned'].cumsum()

    if ('received_amount', 'RESEARCH') in land_df.columns:
        land_df['RESEARCH_earned'] = land_df[('received_amount', 'RESEARCH')]
        result_df['RESEARCH'] = land_df['RESEARCH_earned'].cumsum()

    if ('received_amount', 'SPS') in land_df.columns:
        land_df['SPS_earned'] = land_df[('received_amount', 'SPS')]
        result_df['SPS'] = land_df['SPS_earned'].cumsum()

    # Plot with Plotly Express
    fig = px.line(result_df,
                  x=result_df.index,
                  y=result_df.columns,
                  title='Cumulative sum of the resources',
                  labels={'variable': 'Resource'})

    fig.update_layout(
        template=theme,
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            title="amount (log)",
            type="log",
            exponentformat="none",
            dtick=1,
        ),
    )
    return fig


def plot_tax_cumsum(land_df, theme):
    land_df.columns = land_df.columns.str.replace('_received_tax', '')

    numeric_columns = land_df.select_dtypes(include='number').columns
    land_df_cumsum = land_df[numeric_columns].cumsum()

    fig = px.bar(land_df,
                 x='created_date',
                 y=numeric_columns,
                 barmode='group',
                 title='Received taxes including cumulative sum',
                 labels={'variable': 'Resource'})

    for col in numeric_columns:
        mode = 'lines' if land_df_cumsum[col].size > 1 else 'markers'
        fig.add_scatter(x=land_df.created_date,
                        y=land_df_cumsum[col],
                        mode=mode,
                        name=f'{col} Cumulative Sum')

    fig.update_layout(
        template=theme,
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
        ),
        yaxis=dict(
            title="amount (log)",
            type="log",
            exponentformat="none",
            dtick=1,
        ),
    )
    return fig
