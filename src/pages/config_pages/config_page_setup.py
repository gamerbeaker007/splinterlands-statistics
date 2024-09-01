import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx, State

from src.api import spl
from src.configuration import config
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.utils import store_util
from src.utils.trace_logging import measure_duration

layout = dbc.Row([
    html.H3('Set-up monitoring accounts'),
    dbc.Col([
        html.P(
            [
                'Add the accounts you want to monitor below.',
                html.Br(),
                'You can add multiple accounts by separating them with a comma (,).'
            ]
        ),
        dbc.Row([
            dbc.Col([
                html.Div(
                    className='dbc',
                    children=[
                        dbc.Input(id=config_page_ids.account_name_input,
                                  type='text',
                                  placeholder='account names',
                                  className='m-1 border border-dark',
                                  ),
                        dbc.Button(
                            'Add',
                            id=config_page_ids.add_button,
                            color='primary',
                            className='m-1 mb-3',
                            n_clicks=0
                        ),
                        dbc.Button(
                            'Remove',
                            id=config_page_ids.remove_button,
                            color='danger',
                            className='m-1 mb-3',
                            n_clicks=0
                        ),
                    ]),
            ]),
            html.Div(id=config_page_ids.account_text),
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
def add_remove(add_clicks, account_names):
    text = ''
    added = False
    class_name = 'text-warning'
    if config_page_ids.add_button == ctx.triggered_id:
        if not config.read_only:
            logging.info('Add monitor account button was clicked')
            accounts = [item.strip() for item in account_names.split(',')]

            incorrect_accounts = []
            for account in accounts:
                if not spl.player_exist(account):
                    incorrect_accounts.append(account)

            if len(incorrect_accounts) == 0:
                text = 'Accounts added/updated: ' + ','.join(accounts)
                for account in accounts:
                    store_util.add_account(account)
                    added = True
                    class_name = 'text-success'
            else:
                text = 'Incorrect accounts found: ' + str(','.join(incorrect_accounts))
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
def remove_click(remove_clicks, account_names):
    text = ''
    removed = False
    class_name = 'text-warning'
    if config_page_ids.remove_button == ctx.triggered_id:
        if not config.read_only:
            logging.info('Remove account button was clicked')
            accounts = [item.strip() for item in account_names.split(',')]
            for account in accounts:
                store_util.remove_account(account)
                removed = True
                text = 'Accounts are removed, data is deleted...'
                class_name = 'text-success'
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

    return removed, html.Div(text, className=class_name)
