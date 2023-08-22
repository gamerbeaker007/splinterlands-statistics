import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, State

from main import app
from src import analyse
from src.configuration import store
from src.pages.navigation_pages import nav_ids
from src.pages.nemesis_pages import nemesis_page_ids, nemesis_page_opponent, nemesis_page_battles
from src.static.static_values_enum import MatchType
from src.utils import store_util

layout = dbc.Container([
    dbc.Row(html.H1("Nemesis"), className='mb-3'),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dbc.Select(store_util.get_account_names(),
                               value=store_util.get_first_account_name(),
                               id=nemesis_page_ids.dropdown_user_selection,
                               className='btn-secondary',
                               ),

                ],
            ),
        ),
        dbc.Col(html.H3("VS", style={'text-align': 'center'})),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Against'),
                    dbc.Select(id=nemesis_page_ids.dropdown_against_selection,
                               className='btn-secondary',
                               ),

                ],
            ),
        ),
    ], className='mb-3'),

    dbc.Row([
        dbc.Col(nemesis_page_opponent.layout),
        # dbc.Col(html.H1("COL2 ")),
        # dbc.Col(html.H1("COL3 "), style={'position': 'relative'}),
    ]),

    dbc.Row(html.H3('Last 5 battle')),
    dbc.Row(nemesis_page_battles.layout),

    html.Hr(),
    dbc.Row(dbc.Col(dbc.InputGroup(
        [
            dbc.InputGroupText('Match type'),
            dcc.Dropdown(id=nemesis_page_ids.dropdown_match_type_selection,
                         className='dbc',
                         style={'width': '70%'},
                         ),

        ],
        className='mb-3',
    ),
        md=4,
    )
    ),
    dbc.Row(html.Div(id=nemesis_page_ids.nemesis)),

    dcc.Store(id=nemesis_page_ids.filtered_nemesis_df),
    dcc.Store(id=nemesis_page_ids.filtered_against_df),
])


@app.callback(Output(nemesis_page_ids.dropdown_against_selection, 'value'),
              Output(nemesis_page_ids.dropdown_against_selection, 'options'),
              Input(nemesis_page_ids.dropdown_user_selection, 'value'),
              Input(nav_ids.trigger_daily, 'data'))
def update_account_value(account, daily_trigger):
    players = store_util.get_played_players(account)
    if len(players) > 0:
        return players[0], players
    else:
        return None, None


@app.callback(Output(nemesis_page_ids.dropdown_match_type_selection, 'value'),
              Output(nemesis_page_ids.dropdown_match_type_selection, 'options'),
              Input(nav_ids.trigger_daily, 'data'),
              )
def update_match_types_list(tigger):
    return 'ALL', ['ALL'] + MatchType.list_values()


@app.callback(
    Output(nemesis_page_ids.nemesis, 'children'),
    Input(nemesis_page_ids.filtered_nemesis_df, 'data'),
    State(nemesis_page_ids.dropdown_user_selection, 'value'),
    State(nemesis_page_ids.dropdown_match_type_selection, 'value'),
)
def nemesis(filtered_df, account, match_type):
    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        li = []
        for index, row in filtered_df.iterrows():
            li.append(html.Li(str(row.opponent) + ' (' + str(row.battle_id) + ')'))

        suffix = ''
        if match_type != 'ALL':
            suffix = ' \'' + match_type + '\''

        return dbc.Row([
            html.Br(),
            html.H4(str(account) + '\'s ' + suffix + ' nemesis:'),
            html.Div(children=[html.Ul(children=li)]),
            html.Hr()
        ]),
    else:
        return dbc.Row([
            html.Br(),
            html.Div('NA'),
            html.Hr()
        ]),


@app.callback(Output(nemesis_page_ids.filtered_nemesis_df, 'data'),
              Input(nemesis_page_ids.dropdown_user_selection, 'value'),
              Input(nemesis_page_ids.dropdown_match_type_selection, 'value'),
              )
def filter_nemesis_df(account, filter_match_type):
    df = analyse.get_top_3_losing_account(account, filter_match_type)
    return df.to_json(date_format='iso', orient='split')


@app.callback(Output(nemesis_page_ids.filtered_against_df, 'data'),
              Input(nemesis_page_ids.dropdown_user_selection, 'value'),
              Input(nemesis_page_ids.dropdown_against_selection, 'value'),
              )
def filter_opponent_df(account, opponent):
    df = store.battle_big.loc[(store.battle_big.account == account) & (store.battle_big.opponent == opponent)]
    df = df.drop_duplicates(subset=["battle_id"], keep='first')
    return df.to_json(date_format='iso', orient='split')
