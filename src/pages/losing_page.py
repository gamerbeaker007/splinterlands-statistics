import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc

from src import analyse
from src.pages.main_dash import app
from src.static import static_values_enum
from src.static.static_values_enum import MatchType, CardType
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics losing battles'),
        html.P('Summoners and monster you lose most against'),
        dbc.Col(html.P('Filter on')),
        dbc.Col(dcc.Dropdown(options=['ALL'] + store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        dbc.Col(dcc.Dropdown(options=['ALL'] + static_values_enum.get_list_of_enum(CardType),
                             value='ALL',
                             id='dropdown-type-selection',
                             className='dbc')),
        dbc.Col(dcc.Dropdown(options=['ALL'] + static_values_enum.get_list_of_enum(MatchType),
                             value='ALL',
                             id='dropdown-match-type-selection',
                             className='dbc'))
    ]),
    dbc.Row([
        html.Div(id='battle-count', className='dbc'),
    ]),
    dbc.Row([
        html.Div(id='losing-table', className='dbc'),
    ]),
    dcc.Store(id='filtered-losing-df')

])


@app.callback(
    Output('losing-table', 'children'),
    Input('filtered-losing-df', 'data'),
)
def update_losing_table(filtered_df):
    df = pd.read_json(filtered_df, orient='split')
    if not df.empty:
        df = df[['url', 'card_name', 'level', 'number_of_losses']]
        return dash_table.DataTable(
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns=[
                {'id': 'url', 'name': 'Card', 'presentation': 'markdown'},
                {'id': 'card_name', 'name': 'Name'},
                {'id': 'level', 'name': 'Level'},
                {'id': 'number_of_losses', 'name': 'Numer of losses'},

            ],
            data=df.to_dict('records'),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action='native',
            sort_action='native',
            style_table={'overflowX': 'auto'},
            style_cell_conditional=[{'if': {'column_id': 'url'}, 'width': '200px'}, ],
            page_size=10,
        ),
    else:
        return dash_table.DataTable()


@app.callback(Output('filtered-losing-df', 'data'),
              Output('battle-count', 'children'),
              Input('dropdown-type-selection', 'value'),
              Input('dropdown-user-selection', 'value'),
              Input('dropdown-match-type-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def filter_battle_df(filter_type, filter_user, filter_match_type, trigger_daily):
    df = analyse.get_losing_df(filter_account=filter_user, filter_match_type=filter_match_type, filter_type=filter_type)
    bc = analyse.get_losing_battles_count(filter_user, filter_match_type, filter_type)
    return df.to_json(date_format='iso', orient='split'), \
        html.Div('Battle count: ' + str(bc))
