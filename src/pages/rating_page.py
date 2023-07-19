import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Output, Input
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO

from main import app
from src.configuration import config, store
from src.graphs import rating_graph
from src.static.static_values_enum import Format, MatchType
from src.utils import store_util, chart_util

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(options=['ALL'] + store_util.get_account_names(),
                                 value=store_util.get_first_account_name(),
                                 id='dropdown-user-selection-rating',
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
                dcc.Graph(id='modern-daily-battle-graph'),
            ),
            dbc.Col(
                dcc.Graph(id='wild-daily-battle-graph'),
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


@app.callback(Output('filtered-rating-df', 'data'),
              Output('filtered-daily-df', 'data'),
              Input('dropdown-user-selection-rating', 'value'),
              )
def filter_rating_df(account):
    if account == 'ALL':
        rating_df = store.rating.copy()
        daily_df = store.battle_big.copy()
    else:
        rating_df = store.rating.loc[(store.rating.account == account)].copy()
        daily_df = store.battle_big.loc[(store.battle_big.account == account)].copy()

    if not rating_df.empty:
        rating_df.loc[:].sort_values(by='created_date', inplace=True)

    result_df = pd.DataFrame()
    if not daily_df.empty:
        # Select Ranked battle only
        daily_df = daily_df.loc[(daily_df.match_type == MatchType.RANKED.value)]

        # Select Ranked battles and make dates on day
        daily_df['created_date'] = pd.to_datetime(daily_df.loc[:, 'created_date']).dt.date

        # First group on battle_id
        daily_df = daily_df.groupby(['battle_id'], as_index=False).agg({'result': 'first',
                                                                        'created_date': 'first',
                                                                        'format': 'first'})
        # second group on day
        win_df = daily_df.loc[daily_df.result == 'win'].groupby(
            ['created_date', 'result', 'format'], as_index=False).agg({'result': 'count'})
        loss_df = daily_df.loc[daily_df.result == 'loss'].groupby(
            ['created_date', 'result', 'format'], as_index=False).agg({'result': 'count'})
        result_df = pd.merge(left=win_df, right=loss_df, on=['created_date', 'format'])
        result_df.rename(columns={"result_x": "win", "result_y": "loss"}, inplace=True)
        result_df['battles'] = result_df.win + result_df.loss

    return rating_df.to_json(date_format='iso', orient='split'), result_df.to_json(date_format='iso', orient='split')


@app.callback(Output('wild-daily-battle-graph', 'figure'),
              Input('filtered-daily-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_battle_graph(filtered_df, toggle):
    if not filtered_df:
        raise PreventUpdate
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    filtered_df = pd.read_json(filtered_df, orient='split')
    if filtered_df.empty:
        return chart_util.blank_fig(theme)
    else:
        filtered_df = filtered_df.loc[filtered_df['format'] == Format.WILD.value]
        return rating_graph.plot_daily_stats_battle(filtered_df, theme)


@app.callback(Output('modern-daily-battle-graph', 'figure'),
              Input('filtered-daily-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_battle_graph(filtered_df, toggle):
    if not filtered_df:
        raise PreventUpdate
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    filtered_df = pd.read_json(filtered_df, orient='split')
    if filtered_df.empty:
        return chart_util.blank_fig(theme)
    else:
        filtered_df = filtered_df.loc[filtered_df['format'] == Format.MODERN.value]
        return rating_graph.plot_daily_stats_battle(filtered_df, theme)


@app.callback(Output('modern-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_graph(filtered_df, toggle):
    if not filtered_df:
        raise PreventUpdate

    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.MODERN.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


@app.callback(Output('wild-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_graph(filtered_df, toggle):
    if not filtered_df:
        raise PreventUpdate

    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.WILD.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)
