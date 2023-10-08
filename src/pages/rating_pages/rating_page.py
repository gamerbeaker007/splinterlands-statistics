import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Output, Input
from dash.exceptions import PreventUpdate
from dateutil import parser

from main import app
from src import analyse
from src.configuration import store
from src.graphs import rating_graph
from src.pages.navigation_pages import nav_ids
from src.pages.rating_pages import rating_ids
from src.static.static_values_enum import Format
from src.utils import store_util, chart_util


filter_settings = {}
filter_settings['from_date'] = '2001-01-01T00:00:00.000Z'
filter_settings['account'] = ''

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(id=rating_ids.dropdown_user_selection_rating,
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='m-3',
            ),
            md=4,
        ),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Since season'),
                    dcc.Dropdown(id=rating_ids.since_season_id,
                                 clearable=False,
                                 style={'width': '85px'},
                                 className='dbc'),
                    dbc.InputGroupText(id=rating_ids.filter_from_date)

                ],
                className='m-3',
            ),
        ),

        dbc.Row([
            dbc.Col(
                dcc.Graph(id=rating_ids.daily_battle_graph),
            ),
        ], className='mb-3'),

        html.Center(html.H1("Modern")),
        html.Br(),
        html.Hr(),
        dcc.Graph(id=rating_ids.modern_rating_graph),
        html.Center(html.H1("Wild")),
        dcc.Graph(id=rating_ids.wild_rating_graph),
        dcc.Store(id=rating_ids.filtered_rating_df),
        dcc.Store(id=rating_ids.filtered_daily_df),
        dcc.Store(id=rating_ids.filter_settings),

    ]),
])


@app.callback(Output(rating_ids.dropdown_user_selection_rating, 'value'),
              Output(rating_ids.dropdown_user_selection_rating, 'options'),
              Input(nav_ids.trigger_daily, 'data'),
              )
def update_user_list(tigger):
    return store_util.get_first_account_name(), ['ALL'] + store_util.get_account_names()


@app.callback(Output(rating_ids.filtered_rating_df, 'data'),
              Output(rating_ids.filtered_daily_df, 'data'),
              Input(rating_ids.filter_settings, 'data'),
              )
def filter_df(stored_filter_settings):
    if not stored_filter_settings:
        raise PreventUpdate

    account = stored_filter_settings['account']
    if not account or store.rating.empty or store.battle_big.empty:
        empty_df = pd.DataFrame()
        return empty_df.to_json(date_format='iso', orient='split'), \
            empty_df.to_json(date_format='iso', orient='split')

    if account == 'ALL':
        rating_df = store.rating.copy()
        daily_df = store.battle_big.copy()
    else:
        rating_df = store.rating.loc[(store.rating.account == account)].copy()
        daily_df = store.battle_big.loc[(store.battle_big.account == account)].copy()

    # filter on
    rating_df = analyse.filter_date(rating_df, stored_filter_settings)
    daily_df = analyse.filter_date(daily_df, stored_filter_settings)

    if not rating_df.empty:
        rating_df.loc[:].sort_values(by='created_date', inplace=True)

    result_df = analyse.get_daily_battle_stats(daily_df)

    return rating_df.to_json(date_format='iso', orient='split'), result_df.to_json(date_format='iso', orient='split')


@app.callback(Output(rating_ids.daily_battle_graph, 'figure'),
              Input(rating_ids.filtered_daily_df, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_modern_battle_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if filtered_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return rating_graph.plot_daily_stats_battle(filtered_df, theme)


@app.callback(Output(rating_ids.modern_rating_graph, 'figure'),
              Input(rating_ids.filtered_rating_df, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_modern_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.modern.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


@app.callback(Output(rating_ids.wild_rating_graph, 'figure'),
              Input(rating_ids.filtered_rating_df, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_wild_graph(filtered_df, theme):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.wild.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


@app.callback(Output(rating_ids.since_season_id, 'options'),
              Output(rating_ids.since_season_id, 'value'),
              Input(nav_ids.trigger_daily, 'data'))
def update_seasons_played_list_rating(tigger):
    season_played = store_util.get_seasons_played_list()
    first_played_season = ''
    if len(season_played) > 1:
        first_played_season = season_played[1]
    return season_played, first_played_season


@app.callback(Output(rating_ids.filter_settings, 'data'),
              Output(rating_ids.filter_from_date, 'children'),
              Input(rating_ids.since_season_id, 'value'))
def filter_season_df(season_id):
    if season_id:
        season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
        from_date = parser.parse(season_end_date)

        filter_settings['from_date'] = str(from_date)
        return filter_settings, str(from_date.strftime('%Y-%m-%d %H:%M (UTC)'))
    else:
        return filter_settings, ''


@app.callback(Output(rating_ids.filter_settings, 'data'),
              Input(rating_ids.dropdown_user_selection_rating, 'value'),
              Input(nav_ids.trigger_daily, 'data'),
              )
def filter_battle_df(account,
                     trigger_daily):
    filter_settings['account'] = account
    return filter_settings
