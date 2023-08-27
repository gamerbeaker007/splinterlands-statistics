import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Output, Input
from dash.exceptions import PreventUpdate

from main import app
from src import analyse
from src.configuration import store
from src.graphs import rating_graph
from src.pages.navigation_pages import nav_ids
from src.static.static_values_enum import Format
from src.utils import store_util, chart_util

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(id='dropdown-user-selection-rating',
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id='daily-battle-graph'),
            ),
        ], className='mb-3'),

        html.Center(html.H1("Modern")),
        html.Br(),
        html.Hr(),
        dcc.Graph(id="modern-rating-graph"),
        html.Center(html.H1("Wild")),
        dcc.Graph(id="wild-rating-graph"),
        dcc.Store(id='filtered-rating-df'),
        dcc.Store(id='filtered-daily-df')
    ]),
])


@app.callback(Output('dropdown-user-selection-rating', 'value'),
              Output('dropdown-user-selection-rating', 'options'),
              Input(nav_ids.trigger_daily, 'data'),
              )
def update_user_list(tigger):
    return 'ALL', ['ALL'] + store_util.get_account_names()


@app.callback(Output('filtered-rating-df', 'data'),
              Output('filtered-daily-df', 'data'),
              Input('dropdown-user-selection-rating', 'value'),
              )
def filter_df(account):
    if store.rating.empty or store.battle_big.empty:
        empty_df = pd.DataFrame()
        return empty_df.to_json(date_format='iso', orient='split'), \
            empty_df.to_json(date_format='iso', orient='split')

    if account == 'ALL':
        rating_df = store.rating.copy()
        daily_df = store.battle_big.copy()
    else:
        rating_df = store.rating.loc[(store.rating.account == account)].copy()
        daily_df = store.battle_big.loc[(store.battle_big.account == account)].copy()

    if not rating_df.empty:
        rating_df.loc[:].sort_values(by='created_date', inplace=True)

    result_df = analyse.get_daily_battle_stats(daily_df)

    return rating_df.to_json(date_format='iso', orient='split'), result_df.to_json(date_format='iso', orient='split')


@app.callback(Output('daily-battle-graph', 'figure'),
              Input('filtered-daily-df', 'data'),
              Input('theme-store', 'data'),
              )
def update_modern_battle_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if filtered_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return rating_graph.plot_daily_stats_battle(filtered_df, theme)


@app.callback(Output('modern-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input('theme-store', 'data'),
              )
def update_modern_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.modern.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


@app.callback(Output('wild-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input('theme-store', 'data'),
              )
def update_wild_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.wild.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)
