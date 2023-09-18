import dash_bootstrap_components as dbc
from dash import html, dcc

from src.pages.season import season_ids, season_hive_blog_page, season_battle_info_page, season_balance_info_page, \
    season_update_page

layout = dbc.Container([
    dbc.Row([
        html.H1('Season statistics'),
        dbc.Col(children=season_update_page.layout, className='mb-3'),
        dbc.Col(children=season_hive_blog_page.layout, className='mb-3'),
    ]),
    dbc.Row(children=season_battle_info_page.layout, className='mb-3'),
    dbc.Row(children=season_balance_info_page.layout, className='mb-3'),

    dcc.Store(id=season_ids.trigger_season_update),
])

