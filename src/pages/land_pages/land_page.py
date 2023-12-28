from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dcc

from main import app
from src.configuration import store
from src.graphs import land_graph
from src.pages.land_pages import land_ids
from src.pages.navigation_pages import nav_ids
from src.utils import store_util, chart_util
from src.utils.trace_logging import measure_duration

layout = dbc.Container([
    dcc.Store(id=land_ids.harvest_land_df),
    dcc.Store(id=land_ids.tax_land_df),

    dbc.Row([
        html.H1('Land'),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(id=land_ids.dropdown_user_selection_land,
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),
    ]),
    dbc.Row(
        children=[
            html.H3("Harvest Information"),
            html.P("Note in the graph below the received amount of resources are presented. "
                   "This does not take in account the used grain to harvest"),
            dcc.Graph(id=land_ids.all_graph)
        ], className='mb-3'),
    dbc.Row(children=[
        html.P("In the next graph grain used to harvest is taken into account."),
        dcc.Graph(id=land_ids.cumsum_graph)]
        , className='mb-3'),
    dbc.Row(id=land_ids.tax_row, className='mb-3'),
])


@app.callback(
    Output(land_ids.dropdown_user_selection_land, 'value'),
    Output(land_ids.dropdown_user_selection_land, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_first_account_name(), store_util.get_account_names()


@app.callback(
    Output(land_ids.harvest_land_df, 'data'),
    Input(land_ids.dropdown_user_selection_land, 'value'),
)
@measure_duration
def update_filter_data(account):
    if not store.land.empty:
        # Filter before processing is done
        df = store.land.loc[(store.land.player == account)].copy()
        df.created_date = pd.to_datetime(df.created_date)
        columns = ['received_amount', 'grain_eaten', 'grain_rewards_eaten', 'resource_amount', 'tax_amount']
        temp_df = df.groupby([df.created_date.dt.date, df.resource_symbol, df.player])[columns].sum().reset_index()

        return temp_df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(
    Output(land_ids.tax_land_df, 'data'),
    Input(land_ids.dropdown_user_selection_land, 'value'),
)
@measure_duration
def update_filter_tax_data(account):
    if not store.land.empty:
        # Filter before processing is done
        df = store.land.loc[(store.land.player == account) & (store.land.op == 'tax_collection')].copy()
        if df.empty:
            return None

        df.created_date = pd.to_datetime(df.created_date)
        columns = df.filter(regex='_received_tax')
        temp_df = df.groupby([df.created_date.dt.date])[columns.columns].sum().reset_index()

        return temp_df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(
    Output(land_ids.all_graph, 'figure'),
    Input(land_ids.harvest_land_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_land_total_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return land_graph.plot_land_all(temp_df, theme)


@app.callback(
    Output(land_ids.cumsum_graph, 'figure'),
    Input(land_ids.harvest_land_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_land_total_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return land_graph.plot_cumsum(temp_df, theme)


@app.callback(
    Output(land_ids.tax_row, 'children'),
    Input(land_ids.tax_land_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_land_tax_row(filtered_df, theme):
    if not filtered_df:
        return None
    else:
        temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        fig = land_graph.plot_tax_cumsum(temp_df, theme)
        return [
            html.H3("Castle and Keep tax collections"),
            dcc.Graph(figure=fig),
        ]
