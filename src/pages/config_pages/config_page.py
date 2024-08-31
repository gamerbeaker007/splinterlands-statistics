import dash_bootstrap_components as dbc
from dash import html, dcc

from src.configuration import config
from src.pages.config_pages import config_page_ids, config_page_authorize, config_page_intro, config_page_setup


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
        dbc.Row(children=config_page_setup.layout),
        dbc.Row(children=config_page_intro.layout),
        dbc.Row(id=config_page_ids.authorize_place_holder, children=config_page_authorize.layout),
        dbc.Row(id=config_page_ids.update_account_info),
    ]),
])
