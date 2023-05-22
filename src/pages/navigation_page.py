import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc, ctx
from dash_bootstrap_templates import ThemeSwitchAIO

from main import app
from src import battle_store, collection_store
from src.pages import main_page, rating_page, nemesis_page, losing_page, balance_page, config_page
from src.utils import store_util

SPL_LOGO = 'https://d36mxiodymuqjm.cloudfront.net/website/icons/img_icon_splinterlands.svg'

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=SPL_LOGO, height='150px')),
                        dbc.Col(dbc.NavbarBrand('SPL Battle statistics', className='ms-2')),
                    ],
                    align='center',
                    className='g-0',
                ),
                href='/',
                style={'textDecoration': 'none'},
            ),
            dbc.Col(
                dbc.NavbarSimple(
                    children=[
                        dbc.NavItem(dbc.NavLink('Home', href='/')),
                        dbc.NavItem(dbc.NavLink('Losing', href='/losing')),
                        dbc.NavItem(dbc.NavLink('Rating', href='/rating')),
                        dbc.NavItem(dbc.NavLink('Nemesis', href='/nemesis')),
                        dbc.NavItem(dbc.NavLink('Balance', href='/balance')),
                        dbc.NavItem(dbc.NavLink('Config', href='/config')),
                    ],
                    brand_href='/',
                ),
            ),
            dbc.Col(
                ThemeSwitchAIO(aio_id="theme",
                               themes=[dbc.themes.MINTY, dbc.themes.CYBORG],
                               switch_props={'value': False}),
                width='auto'),
            dbc.Col(
                dbc.Button(
                    'Pull new data',
                    id='load-new-values',
                    color='primary',
                    className='ms-2', n_clicks=0
                ),
                width='auto',
            ),
            html.Div(id='hidden-div', style={'display': 'none'}),
            html.Div(id='hidden-div1', style={'display': 'none'}),

        ]),
)

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[]),
])


@app.callback(Output('page-content', 'children'),
          [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return main_page.layout
    if pathname == '/losing':
        return losing_page.layout
    if pathname == '/rating':
        return rating_page.layout
    if pathname == '/nemesis':
        return nemesis_page.layout
    if pathname == '/balance':
        return balance_page.layout
    if pathname == '/config':
        return config_page.layout
    else:  # if redirected to unknown link
        return '404 Page Error! Please choose a link'


@app.callback(
    Output('hidden-div1', 'children'),
    Input('load-new-values', 'n_clicks'),
)
def update_output(n_clicks):
    if "load-new-values" == ctx.triggered_id:
        logging.info("Update battle button pressed")
        collection_store.update_collection()
        battle_store.process_battles()

        store_util.save_stores()

