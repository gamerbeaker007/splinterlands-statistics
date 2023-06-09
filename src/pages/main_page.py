import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc

from main import app
from src import analyse
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics battles'),
        html.P('Your battle statistics of your summoners and monster'),
        dbc.Col(html.P('Filter on')),
        dbc.Col(dcc.Dropdown(store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
    ]),
    dbc.Row([
        html.Div(id='main-table', className='dbc'),
    ]),
    dcc.Store(id='filtered-battle-df')

])


@app.callback(
    Output('main-table', 'children'),
    Input('filtered-battle-df', 'data'),
)
def update_main_table(filtered_df):
    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        return dash_table.DataTable(
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns=[
                {'id': 'url', 'name': 'Card', 'presentation': 'markdown'},
                {'id': 'card_name', 'name': 'Name'},
                {'id': 'level', 'name': 'Level'},
                # {'id': 'win_to_loss_ratio', 'name': 'win_to_loss_ratio'},
                {'id': 'battles', 'name': 'Battles'},
                # {'id': 'win_ratio', 'name': 'win_ratio'},
                {'id': 'win_percentage', 'name': 'Win Percentage'},
            ],
            data=filtered_df.to_dict('records'),
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


@app.callback(Output('filtered-battle-df', 'data'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def filter_battle_df(account, trigger_daily):
    df = analyse.get_my_battles_df(account)
    return df.to_json(date_format='iso', orient='split')
