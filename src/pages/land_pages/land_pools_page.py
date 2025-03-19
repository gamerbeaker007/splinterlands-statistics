from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dcc

from src.configuration import store
from src.graphs import land_graph
from src.pages.land_pages import land_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

layout = dbc.Row(
    children=[
        html.H3("Trade hub, land pools "),
        html.P("View your deposited resources and value."),
        html.Div(id=land_ids.land_pools_container)
    ],
    className='mb-3'),


@app.callback(
    Output(land_ids.land_pools_df, 'data'),
    Input(land_ids.dropdown_user_selection_land, 'value'),
)
@measure_duration
def update_land_pool_filter_data(account):
    if not store.land_pools.empty:
        # Filter before processing is done
        df = store.land_pools.loc[(store.land_pools.account_name == account)].copy()
        return df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(
    Output(land_ids.land_pools_container, 'children'),
    Input(land_ids.land_pools_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_land_pools_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)

    temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)

    # Get multiple figures (one per token)
    figures_dict = land_graph.plot_land_pools(temp_df, theme)

    # Generate a list of dcc.Graph components dynamically
    graph_components = [
        dcc.Graph(
            id=f'land-pool-graph-{token}',
            figure=fig
        ) for token, fig in figures_dict.items()
    ]

    return graph_components  # Return the list of graphs
