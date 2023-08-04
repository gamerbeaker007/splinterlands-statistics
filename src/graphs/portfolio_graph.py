import plotly.colors as pc
import plotly.express as px
import plotly.graph_objects as go

from src.static.static_values_enum import Edition


def plot_portfolio_total(portfolio_df, combined_users, theme):
    portfolio_df.sort_values('date', inplace=True)
    if 'total_investment_value' in portfolio_df.columns.tolist():
        column_data = portfolio_df[['total_value', 'total_investment_value']].columns
    else:
        column_data = portfolio_df[['total_value']].columns

    fig = px.line(portfolio_df,
                  x='date',
                  y=column_data,
                  title="Total portfolio values of '" + ",".join(combined_users) + "' combined",
                  markers=True)
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig


def plot_portfolio_all(df, theme, skip_zero=True):
    temp_df = df.drop('account_name', axis=1)

    if skip_zero:
        temp_df = temp_df.drop('date', axis=1)
        temp_df = temp_df.loc[:, (temp_df.sum(axis=0) != 0.0)]
        temp_df['date'] = df[['date']]

    fig = px.line(temp_df,
                  x=temp_df.date,
                  y=temp_df.columns,
                  title="All items",
                  markers=True)
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig


def get_editions_fig(editions_df, theme):
    fig = go.Figure()
    max_value = editions_df.loc[:, editions_df.columns.str.endswith("_market_value")].max().max()
    max_bcx = editions_df.loc[:, editions_df.columns.str.endswith("_bcx")].max().max()

    # Get a discrete color palette from Plotly
    color_palette = pc.qualitative.Plotly
    color_index = 0  # Initialize the index for cycling colors

    for edition in Edition.list_names():
        if str(edition) + "_bcx" in editions_df.columns.tolist():
            legend_group = edition
            current_color = color_palette[color_index]

            market_value_trace = go.Scatter(x=editions_df.index,
                                            y=editions_df[str(edition) + '_market_value'],
                                            mode='lines',
                                            legendgroup=legend_group,
                                            line=dict(color=current_color),  # Set line color
                                            name=str(edition))
            fig.add_trace(market_value_trace)
            bcx__trace = go.Scatter(x=editions_df.index,
                                    y=editions_df[str(edition) + '_bcx'],
                                    mode='lines',
                                    legendgroup=legend_group,
                                    showlegend=False,
                                    line=dict(color=current_color, dash='dash'),
                                    name=str(edition) + ' bcx',
                                    yaxis='y2')
            fig.add_trace(bcx__trace)
            color_index = (color_index + 1) % len(color_palette)  # Move to the next color

    fig.update_layout(
        template=theme,
        title_text="Editions",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            title='date'
        ),

        yaxis2=dict(
            overlaying='y',
            side='right',
            position=1.0,  # Adjust the position of the secondary y-axis
            range=[0, max_bcx * 1.05],
            title='bcx',
        ),
        yaxis1=dict(
            showgrid=False,
            range=[0, max_value * 1.05],
            title="value $",
        ),
    )

    return fig
