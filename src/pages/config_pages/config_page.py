import dash_bootstrap_components as dbc
from dash import html, dcc

from src.configuration import config
from src.pages.config_pages import config_page_ids, config_page_authorize, config_page_intro, config_page_setup, \
    config_page_accounts_overview
from src.pages.shared_modules import styles


def get_readonly_text():
    if config.read_only:
        return html.H4("Read only mode... Not possible to modify accounts.", className='text-warning')
    return ""


layout = dbc.Container([
    dcc.Store(id=config_page_ids.account_added),
    dcc.Store(id=config_page_ids.account_updated),
    dcc.Store(id=config_page_ids.account_removed),

    dbc.Row([
        dbc.Row(children=get_readonly_text()),
        dbc.Row(config_page_setup.layout, style=styles.get_read_only_mode_style()),
        dbc.Row(children=config_page_accounts_overview.get_layout()),

        html.Hr(className="mt-3"),
        dbc.Row(children=config_page_intro.layout),
        dbc.Row(children=config_page_authorize.layout, style=styles.get_read_only_mode_style()),
    ]),
])
