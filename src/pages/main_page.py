import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc, ctx, State
from dash.exceptions import PreventUpdate

from main import app
from src import analyse
from src.pages import filter_page
from src.static.static_values_enum import Element, Edition, CardType
from src.utils import store_util

btn_active_style = '#222'
btn_inactive_style = '#bdbfbe'

filter_settings = {}
for element in Element:
    filter_settings[element.name] = False
for edition in Edition:
    filter_settings[edition.name] = False
for card_type in CardType:
    filter_settings[card_type.name] = False

filter_settings['account'] = ''

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
        dbc.Col(html.H4('Filter Bar')),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(CardType))),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(Element))),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(Edition))),
        dbc.Col(
            [
                html.Div(id='filter-output')
            ]
        ),

    ]),
    dbc.Row([
        html.Div(id='main-table', className='dbc'),
    ]),
    dcc.Store(id='filtered-battle-df'),
    dcc.Store(id='filter-settings'),
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
              Input('filter-settings', 'data'))
def filter_battle_df(store_filter_settings):
    if store_filter_settings is None or store_filter_settings['account'] == '':
        raise PreventUpdate

    df = analyse.get_my_battles_df(store_filter_settings['account'])
    df = analyse.filter_out_element(df, filter_settings)
    df = analyse.filter_out_edition(df, filter_settings)
    df = analyse.filter_out_card_type(df, filter_settings)
    return df.to_json(date_format='iso', orient='split')


@app.callback(Output('filter-settings', 'data'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def filter_battle_df(account,
                     trigger_daily):
    filter_settings['account'] = account
    return filter_settings


for element in Element:
    @app.callback(Output('{}-filter-button'.format(element.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(element.name), 'n_clicks'),
                  State('{}-filter-button'.format(element.name), 'style')
                  )
    def on_click(n_clicks, style):
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        class_name = btn_active_style if is_active(n_clicks) else btn_inactive_style
        filter_settings[setting] = is_active(n_clicks)
        style['background-color'] = class_name
        return style, filter_settings

for edition in Edition:
    @app.callback(Output('{}-filter-button'.format(edition.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(edition.name), 'n_clicks'),
                  State('{}-filter-button'.format(edition.name), 'style')
                  )
    def on_click(n_clicks, style):
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        class_name = btn_active_style if is_active(n_clicks) else btn_inactive_style
        filter_settings[setting] = is_active(n_clicks)
        style['background-color'] = class_name

        return style, filter_settings

for card_type in CardType:
    @app.callback(Output('{}-filter-button'.format(card_type.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(card_type.name), 'n_clicks'),
                  State('{}-filter-button'.format(card_type.name), 'style')
                  )
    def on_click(n_clicks, style):
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        class_name = btn_active_style if is_active(n_clicks) else btn_inactive_style
        filter_settings[setting] = is_active(n_clicks)
        style['background-color'] = class_name
        return style, filter_settings


def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False
