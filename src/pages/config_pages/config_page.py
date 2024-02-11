import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx, dcc, State

from src.api import spl
from src.configuration import config
from src.pages.config_pages import config_page_ids, config_page_authorize, config_page_spl_api_ckeck
from src.pages.main_dash import app
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_readonly_style():
    if config.read_only:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def get_readonly_text():
    if config.read_only:
        return html.H4("Read only mode not possible to modify accounts", className='text-warning')
    return ""


layout = dbc.Container([
    dbc.Row([
        html.H1('Add and remove accounts'),
        html.P('Current accounts that are being monitored: '),
        html.Div(id=config_page_ids.current_accounts),
        dbc.Row([
            dbc.Col([
                html.Div(
                    style=get_readonly_style(),
                    className='dbc',
                    children=[
                        dbc.Input(id=config_page_ids.account_name_input,
                                  type='text',
                                  placeholder='account-name',
                                  className='m-1 border border-dark',
                                  style={"width": "20%"},
                                  ),
                        dbc.Button(
                            'Add',
                            id=config_page_ids.add_button,
                            color='primary',
                            className='m-1',
                            n_clicks=0
                        ),
                        dbc.Button(
                            'Remove',
                            id=config_page_ids.remove_button,
                            color='danger',
                            className='m-1',
                            n_clicks=0
                        ),
                    ]),
            ]),
            html.Div(children=get_readonly_text()),
            html.Div(id=config_page_ids.account_text),
            dbc.Row(config_page_authorize.get_layout(), style=get_readonly_style()),
            dbc.Row(id=config_page_ids.update_account_info),

            dcc.Store(id=config_page_ids.account_added),
            dcc.Store(id=config_page_ids.account_updated),
            dcc.Store(id=config_page_ids.account_removed)
        ]),
    ]),
])


@app.callback(
    Output(config_page_ids.account_added, 'data'),
    Output(config_page_ids.account_text, 'children'),
    Input(config_page_ids.add_button, 'n_clicks'),
    State(config_page_ids.account_name_input, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def add_remove(add_clicks, account_name):
    text = ''
    added = False
    class_name = 'text-warning'
    if config_page_ids.add_button == ctx.triggered_id:
        if not config.read_only:
            logging.info('Add account button was clicked')
            if spl.player_exist(account_name):
                store_util.add_account(account_name)
                added = True
                text = 'Account added, started daily update...'
                class_name = 'text-success'
            else:
                text = 'Account not added no splinterlands account found for: ' + str(account_name)
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

    return added, html.Div(text, className=class_name)


@app.callback(
    Output(config_page_ids.account_removed, 'data'),
    Output(config_page_ids.account_text, 'children'),
    Input(config_page_ids.remove_button, 'n_clicks'),
    State(config_page_ids.account_name_input, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def add_remove(remove_clicks, account_name):
    text = ''
    removed = False
    class_name = 'text-warning'
    if config_page_ids.remove_button == ctx.triggered_id:
        if not config.read_only:
            logging.info('Remove account button was clicked')
            store_util.remove_account(account_name)
            removed = True
            text = 'Account removed, data is deleted...'
            class_name = 'text-success'
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

    return removed, html.Div(text, className=class_name)


@app.callback(
    Output(config_page_ids.current_accounts, 'children'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
)
@measure_duration
def get_accounts(added, removed):
    current_account_names = store_util.get_account_names()
    return html.P(', '.join(current_account_names))


# @app.callback(
#     Input(config_page_ids.account_added, 'data'),
# )
# @measure_duration
# def update_daily(added):
#     if added:
#         store_util.update_data(battle_update=True, season_update=False)


@app.callback(
    Output(config_page_ids.update_account_info, 'children'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
    Input(config_page_ids.account_updated, 'data'),
)
@measure_duration
def update_check_accounts(added, removed, updated):
    return config_page_spl_api_ckeck.get_layout()
