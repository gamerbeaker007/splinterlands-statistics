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
    children, color = check_spl_api()

    return dbc.Row([
        dbc.Col(
            dbc.Alert(
                children=children,
                color=color,
                style={'height': '38px'},
                className='p-2'),
        )
    ])


def check_spl_api():
    token_dict = store_util.get_token_dict()
    if spl.verify_token(token_dict):
        children = [
            html.I(className='m-1 fas fa-check-circle'),
            'Connected to splinterlands API with account ' + str(token_dict['username'])
        ]
        color = 'success'
    else:
        children = [html.I(className='m-1 fas fa-exclamation-triangle'),
                    'Not connected to splinterlands API']
        color = 'warning'
    return children, color
