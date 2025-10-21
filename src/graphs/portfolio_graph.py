import plotly.colors as pc
import plotly.express as px
import plotly.graph_objects as go

from src.static.static_values_enum import edition_mapping

DEFAULT_HEIGHT = 800


def plot_portfolio_total(portfolio_df, combined_users, theme):
    portfolio_df.sort_values('date', inplace=True)
    if 'total_investment_value' in portfolio_df.columns.tolist() \
            and not portfolio_df['total_investment_value'].dropna().empty:
        column_data = portfolio_df[['total_value', 'total_investment_value']].columns

        # add last investment value to the last row for visual effect
        last_investment_value = portfolio_df['total_investment_value'].dropna().tolist()[-1]
        portfolio_df.loc[portfolio_df.index[-1], 'total_investment_value'] = last_investment_value
    else:
        column_data = portfolio_df[['total_value']].columns

    fig = px.line(portfolio_df,
                  x='date',
                  y=column_data,
                  title='Total portfolio values of \'' + ','.join(combined_users) + '\' combined',
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
    fig = go.Figure()

    temp_df = df.drop('account_name', axis=1)

    if skip_zero:
        temp_df = temp_df.drop('date', axis=1)
        temp_df = temp_df.loc[:, (temp_df.sum(axis=0) != 0.0)]
        temp_df['date'] = df[['date']]

    temp_df = temp_df.set_index('date')
    max_value = temp_df.loc[:, temp_df.columns.str.endswith('_value')].max().max()
    max_qty = temp_df.loc[:, ~temp_df.columns.str.endswith('_value')].max().max()

    # Get a discrete color palette from Plotly
    color_palette = pc.qualitative.Plotly
    color_index = 0  # Initialize the index for cycling colors

    # Sort columns for legend
    temp_df = temp_df.reindex(sorted(temp_df.columns), axis=1)
    for column in temp_df.columns.tolist():
        current_color = color_palette[color_index]

        mode = 'lines' if temp_df[column].size > 1 else 'markers'
        if '_value' in column:
            trace = go.Scatter(x=temp_df.index,
                               y=temp_df[column],
                               mode=mode,
                               connectgaps=True,
                               # legendgroup=legend_group,
                               # showlegend=False,
                               line=dict(color=current_color),
                               name=column)
        else:
            trace = go.Scatter(x=temp_df.index,
                               y=temp_df[column],
                               mode=mode,
                               connectgaps=True,
                               # legendgroup=legend_group,
                               line=dict(color=current_color, dash='dash'),
                               name=column,
                               yaxis='y2')
        fig.add_trace(trace)
        color_index = (color_index + 1) % len(color_palette)  # Move to the next color

    fig.update_layout(
        template=theme,
        title_text='All',
        legend=dict(
            orientation='v',
            x=1.1,
            xanchor='left',
            y=1,
            font=dict(
                size=10
            ),
            borderwidth=1,
        ),
        xaxis=dict(
            title='date'
        ),

        yaxis2=dict(
            overlaying='y',
            side='right',
            position=1.0,  # Adjust the position of the secondary y-axis
            range=[0, max_qty * 1.05],
            title='qty/bcx/count',
        ),
        yaxis1=dict(
            showgrid=False,
            range=[0, max_value * 1.05],
            title='value $',
        ),
        height=DEFAULT_HEIGHT,
    )

    return fig


def get_editions_fig(editions_df, theme):
    fig = go.Figure()
    # max_value = editions_df.loc[:, editions_df.columns.str.endswith('_market_value')].max().max()
    # max_bcx = editions_df.loc[:, editions_df.columns.str.endswith('_bcx')].max().max()

    # Get a discrete color palette from Plotly
    color_palette = pc.qualitative.Plotly
    color_index = 0  # Initialize the index for cycling colors

    for edition in edition_mapping.keys():
        if str(edition) + '_bcx' in editions_df.columns.tolist():
            legend_group = edition
            current_color = color_palette[color_index]

            mode = 'lines' if editions_df[str(edition) + '_market_value'].size > 1 else 'markers'
            market_value_trace = go.Scatter(x=editions_df.index,
                                            y=editions_df[str(edition) + '_market_value'],
                                            mode=mode,
                                            legendgroup=legend_group,
                                            line=dict(color=current_color),  # Set line color
                                            name=str(edition_mapping.get(edition)))
            fig.add_trace(market_value_trace)
            mode = 'lines' if editions_df[str(edition) + '_bcx'].size > 1 else 'markers'
            bcx__trace = go.Scatter(x=editions_df.index,
                                    y=editions_df[str(edition) + '_bcx'],
                                    mode=mode,
                                    legendgroup=legend_group,
                                    showlegend=False,
                                    line=dict(color=current_color, dash='dash'),
                                    name=str(edition_mapping.get(edition)) + ' bcx',
                                    yaxis='y2')
            fig.add_trace(bcx__trace)
            color_index = (color_index + 1) % len(color_palette)  # Move to the next color

    current_color = color_palette[color_index]
    temp_df = editions_df.copy()
    temp_df['all_value'] = temp_df.loc[:, temp_df.columns.str.endswith('_market_value')].sum(axis=1)
    temp_df['all_bcx'] = temp_df.loc[:, temp_df.columns.str.endswith('_bcx')].sum(axis=1)
    legend_group = 'combined'
    mode = 'lines' if temp_df.all_value.size > 1 else 'markers'
    market_value_trace = go.Scatter(x=temp_df.index,
                                    y=temp_df.all_value,
                                    mode=mode,
                                    legendgroup=legend_group,
                                    line=dict(color=current_color),  # Set line color
                                    name=legend_group)
    fig.add_trace(market_value_trace)
    mode = 'lines' if temp_df.all_bcx.size > 1 else 'markers'
    bcx__trace = go.Scatter(x=temp_df.index,
                            y=temp_df.all_bcx,
                            mode=mode,
                            legendgroup=legend_group,
                            showlegend=False,
                            line=dict(color=current_color, dash='dash'),
                            name=legend_group + ' bcx',
                            yaxis='y2')
    fig.add_trace(bcx__trace)

    fig.update_layout(
        template=theme,
        title_text='Editions',
        hovermode='x unified',
        margin=dict(l=10, r=10),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            title='date'
        ),

        yaxis2=dict(
            overlaying='y',
            side='right',
            position=1.0,  # Adjust the position of the secondary y-axis
            # range=[0, max_bcx * 1.05],
            title='bcx',
        ),
        yaxis1=dict(
            showgrid=False,
            # range=[0, max_value * 1.05],
            title='value $',
        ),
        height=DEFAULT_HEIGHT,

    )

    return fig


def get_sps_fig(sps_df, theme):
    fig = go.Figure()
    max_value = sps_df.loc[:, sps_df.columns.str.endswith('_value')].max().max()
    max_qty = sps_df.loc[:, sps_df.columns.str.endswith('_qty')].max().max()

    # Get a discrete color palette from Plotly
    color_palette = pc.qualitative.Plotly
    color_index = 0  # Initialize the index for cycling colors

    for column in sps_df.columns.tolist():
        current_color = color_palette[color_index]
        legend_group = 'spsp' if 'spsp' in column else 'sps'

        mode = 'lines' if sps_df[column].size > 1 else 'markers'
        if '_qty' in column:
            trace = go.Scatter(x=sps_df.index,
                               y=sps_df[column],
                               mode=mode,
                               legendgroup=legend_group,
                               showlegend=False,
                               line=dict(color=current_color, dash='dash'),
                               name=legend_group + ' qty ',
                               yaxis='y2')
        else:
            trace = go.Scatter(x=sps_df.index,
                               y=sps_df[column],
                               mode=mode,
                               legendgroup=legend_group,
                               line=dict(color=current_color),  # Set line color
                               name=legend_group)
        fig.add_trace(trace)
        color_index = (color_index + 1) % len(color_palette)  # Move to the next color

    fig.update_layout(
        template=theme,
        title_text='SPS',
        hovermode='x unified',
        margin=dict(l=10, r=10),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            title='date'
        ),

        yaxis2=dict(
            overlaying='y',
            side='right',
            position=1.0,  # Adjust the position of the secondary y-axis
            range=[0, max_qty * 1.05],
            title='qty',
        ),
        yaxis1=dict(
            showgrid=False,
            range=[0, max_value * 1.05],
            title='value $',
        ),
        height=DEFAULT_HEIGHT,
    )

    return fig
