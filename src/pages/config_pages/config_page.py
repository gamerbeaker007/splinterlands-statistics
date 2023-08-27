import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx, dcc

from main import app
from src.api import spl
from src.configuration import config
from src.pages.config_pages import config_page_ids
from src.utils import store_util


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
                html.Div(id=config_page_ids.button_div, style=get_div_style(),
                         children=[
                             dbc.Input(id=config_page_ids.account_name_input,
                                       type='text',
                                       placeholder='account-name',
                                       className='m-1',
                                       style={'marginRight': '10px'}),
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
            html.Div(id=config_page_ids.error_text_account),
            dcc.Store(id=config_page_ids.accounts_updated)

        ]),
    ]),
])


@app.callback(
    Output(config_page_ids.accounts_updated, 'data'),
    Output(config_page_ids.error_text_account, 'children'),
    Input(config_page_ids.account_name_input, 'value'),
    Input(config_page_ids.add_button, 'n_clicks'),
    Input(config_page_ids.remove_button, 'n_clicks'),
)
def add_remove(account_name, add_clicks, remove_clicks):
    error_text = ''
    updated = False

    if config_page_ids.add_button == ctx.triggered_id:
        error_text = ''
        logging.info('Add account button was clicked')
        if spl.player_exist(account_name):
            store_util.add_account(account_name)
            updated = True
        else:
            error_text = 'Account not added no splinterlands account found for: ' + str(account_name)
    if config_page_ids.remove_button == ctx.triggered_id:
        logging.info('Remove account button was clicked')
        store_util.remove_account(account_name)
        updated = True
    return updated, html.Div(error_text, className='text-warning')


@app.callback(
    Output(config_page_ids.current_accounts, 'children'),
    Input(config_page_ids.accounts_updated, 'data'),
)
def get_accounts(updated):
    current_account_names = store_util.get_account_names()
    return html.P(', '.join(current_account_names))
