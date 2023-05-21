import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx

from main import app
from src.api import spl
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Add and remove accounts'),
        html.P("Current account monitored: "),
        html.Div(id='current-accounts'),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="account-name-input", type="text", placeholder="account-name",
                          style={'marginRight': '10px'}),
                dbc.Button(
                    'Add',
                    id='add-account-btn',
                    color='primary',
                    className='ms-2', n_clicks=0
                ),
                dbc.Button(
                    'Remove',
                    id='remove-account-btn',
                    color='danger',
                    className='ms-2', n_clicks=0
                ),
            ]),
            html.Div(id='error-text-account'),
        ]),
    ]),
])


@app.callback(
    Output('current-accounts', 'children'), Output('error-text-account', "children"),
    Input('account-name-input', 'value'),
    Input('add-account-btn', 'n_clicks'),
    Input('remove-account-btn', 'n_clicks'),
)
def add_remove(account_name, add_clicks, remove_clicks):
    current_account_names = store_util.get_account_names()
    error_text = ""
    if "add-account-btn" == ctx.triggered_id:
        logging.info("Add account button was clicked")
        if spl.player_exist(account_name):
            current_account_names = store_util.add_account(account_name)
        else:
            error_text = "Account not added no splinterlands account found for: " + str(account_name)
    if "remove-account-btn" == ctx.triggered_id:
        logging.info("Remove account button was clicked")
        current_account_names = store_util.remove_account(account_name)
    return html.P(",".join(current_account_names)), html.Div(error_text, className="text-warning")
