import dash_bootstrap_components as dbc
from dash import html, dcc

from src.pages.season_pages import season_ids, season_update_page, season_hive_blog_page, season_battle_info_page, \
    season_balance_info_page

layout = dbc.Container([
    dbc.Row([
        html.H2('Season statistics'),
        dbc.Col(children=season_update_page.layout, className='mb-3'),
        dbc.Col(children=season_hive_blog_page.layout, className='mb-3'),
        dbc.Row(html.Hr()),
        dbc.Row(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(id=season_ids.dropdown_user_selection_season,
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),
                ],
                className='mb-3',
            )
        ),

    ]),
    dbc.Row(children=season_battle_info_page.layout, className='mb-3'),
    dbc.Row(children=season_balance_info_page.layout, className='mb-3'),

    dcc.Store(id=season_ids.trigger_season_update),
])
