import logging

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, ctx, dcc, State

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_div_style():
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
        html.P('Current account monitored: '),
        html.Div(id=config_page_ids.current_accounts),
        dbc.Row([
            dbc.Col([
                html.Div(id=config_page_ids.button_div,
                         style=get_div_style(),
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

            dbc.Row(
                dbc.Col(style=get_div_style(),
                        className='dbc',
                        children=[
                            dbc.Input(id=config_page_ids.username_input,
                                      type='text',
                                      placeholder='username',
                                      style={"width": "20%"},
                                      className='m-1 border border-dark'),
                            dbc.Input(id=config_page_ids.version_input,
                                      type='text',
                                      placeholder='version',
                                      style={"width": "20%"},
                                      className='m-1 border border-dark'),
                            dbc.Input(id=config_page_ids.token_input,
                                      type='text',
                                      placeholder='token',
                                      style={"width": "20%"},
                                      className='m-1 border border-dark'),
                        ]),
            ),
            dbc.Row([
                dbc.Col(
                    dbc.Button(
                        'Update token info',
                        id=config_page_ids.update_button,
                        style=get_div_style(),
                        color='primary',
                        className='m-1',
                        n_clicks=0
                    ),
                    width=2
                ),
                dbc.Col(
                    dbc.Alert(id=config_page_ids.alert,
                              style={"height": "38px"},
                              className="p-2"),
                    width=4
                ),
            ]),

            dbc.Row([
                dbc.Col([
                ]),
            ]),
            html.Div(id=config_page_ids.secrets_text),

            dcc.Store(id=config_page_ids.account_added),
            dcc.Store(id=config_page_ids.account_removed)
        ]),
    ]),
])


@app.callback(
    Output(config_page_ids.account_added, 'data'),
    Output(config_page_ids.account_text, 'children'),
    Input(config_page_ids.account_name_input, 'value'),
    Input(config_page_ids.add_button, 'n_clicks'),
)
@measure_duration
def add_remove(account_name, add_clicks):
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
    Input(config_page_ids.account_name_input, 'value'),
    Input(config_page_ids.remove_button, 'n_clicks'),
)
@measure_duration
def add_remove(account_name, remove_clicks):
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


@app.callback(
    Input(config_page_ids.account_added, 'data'),
)
@measure_duration
def update_daily(added):
    if added:
        store_util.update_data(battle_update=True, season_update=False)


@app.callback(
    Output(config_page_ids.secrets_text, 'children'),
    Input(config_page_ids.update_button, 'n_clicks'),
    State(config_page_ids.username_input, 'value'),
    State(config_page_ids.version_input, 'value'),
    State(config_page_ids.token_input, 'value'),
)
@measure_duration
def update_remove(n_clicks, username, version, token):
    if config_page_ids.update_button == ctx.triggered_id:
        if not config.read_only:
            if username and version and token:
                data = [[username, version, token]]
                df = pd.DataFrame(data, columns=['username', 'version', 'token'])
                store.secrets = df
                store_util.save_single_store('secrets')
                return html.Div("Stored", className='text-success')

            return html.Div("Invalid / incomplete info", className='text-warning')
        else:
            text = 'This is not allowed in read-only mode'
            return html.Div(text, className='text-danger')


@app.callback(
    Output(config_page_ids.alert, 'children'),
    Output(config_page_ids.alert, 'color'),
    Input(config_page_ids.update_button, 'n_clicks'),
)
@measure_duration
def update_alert(n_clicks):
    battles = spl.get_battle_history_df(store_util.get_first_account_name())
    if battles is not None:
        children = [html.I(className="m-1 fas fa-check-circle"), "SPL API OK."]
        color = "success"
    else:
        children = [html.I(className="m-1 fas fa-exclamation-triangle"),
                    "SPL API unreachable provide token information"]
        color = "warning"

    return children, color
