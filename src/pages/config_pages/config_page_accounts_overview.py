import dash_bootstrap_components as dbc
from dash import Output, Input
from dash import html

from src.api import spl
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.static import static_values_enum
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_account_status_row(account):
    children, color = get_status(account)
    return dbc.Col([
        html.Img(
            src=static_values_enum.helm_icon_url,
            className='m-1'
        ),
        html.Label(
            account,
            className='m-1 p-1 border border-dark',
            style={"width": "20%"},
        ),
        html.Label(children=children, className=color, style={'display': 'inline-block'})

    ])


def get_status(account):
    token_dict = store_util.get_token_dict(account)
    if spl.verify_token(token_dict):
        children = [
            html.I(className='m-1 fas fa-check-circle'),
            'Connected to Splinterlands API'
        ]
        color = 'text-success'
    else:
        children = [
            html.I(className='m-1 fas fa-exclamation-triangle'),
            'Not connected to Splinterlands API'
        ]
        color = 'text-warning'

    return children, color


def get_layout():
    return dbc.Row(id=config_page_ids.accounts_overview)


@app.callback(
    Output(config_page_ids.accounts_overview, 'children'),
    Input(config_page_ids.account_added, 'data'),
    Input(config_page_ids.account_removed, 'data'),
    Input(config_page_ids.account_updated, 'data'),
)
@measure_duration
def update_status_field(added, removed, updated):
    rows = [html.H5("Configured accounts ")]
    accounts = store_util.get_account_names()
    if accounts:
        for account in accounts:
            temp = get_account_status_row(account)
            rows.append(dbc.Row(temp))
    else:
        rows.append(html.Li("None"))
    return rows
