import pandas as pd
import plotly.express as px


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
        fig.add_scatter(x=land_df.created_date,
                        y=land_df_cumsum[col],
                        mode='lines',
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
