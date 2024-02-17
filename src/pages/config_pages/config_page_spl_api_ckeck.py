import dash_bootstrap_components as dbc
from dash import html

from src.api import spl
from src.utils import store_util


def get_layout():
    info_text = [
        'Posting keys are required for battle history and season earning.',
        html.Br(),
        'With this posting the spl token is retrieved and stored locally in secrets.csv.',
        html.Br(),
        'Posting keys are not stored.',
        html.Br(),
        'Information like portfolio and land are currently still public information.'
    ]
    rows = [
        dbc.Row(html.H3('Accounts status overview', className='mt-5')),
        dbc.Row(html.P(info_text, className='')),
    ]
    for account in store_util.get_account_names():
        children, color = check_spl_api(account)
        rows.append(
            dbc.Row([
                dbc.Col(
                    dbc.Alert(
                        children=children,
                        color=color,
                        style={'height': '38px'},
                        className='p-2'),
                )
            ])
        )
    return rows


def check_spl_api(account):
    if spl.verify_token(store_util.get_token_as_params_string(account)):
        children = [html.I(className='m-1 fas fa-check-circle'), str(account) + ' - connected']
        color = 'success'
    else:
        children = [html.I(className='m-1 fas fa-exclamation-triangle'),
                    str(account) + ' - not connected, provide token information']
        color = 'warning'
    return children, color
