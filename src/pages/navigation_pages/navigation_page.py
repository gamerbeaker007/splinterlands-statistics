import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_extensions.enrich import Trigger
from dash_iconify import DashIconify

from main import app
from src.configuration import progress, config
from src.pages import main_page, rating_page, losing_page, season_page, config_pages
from src.pages.card_pages import card_page, card_page_filter
from src.pages.config_pages import config_page
from src.pages.navigation_pages import nav_ids, navigation_page_update
from src.pages.nemesis_pages import nemesis_page
from src.pages.portfolio_pages import portfolio_page

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
                        dbc.NavItem(dbc.NavLink('Card', href='/card')),
                        dbc.NavItem(dbc.NavLink('Rating', href='/rating')),
                        dbc.NavItem(dbc.NavLink('Nemesis', href='/nemesis')),
                        dbc.NavItem(dbc.NavLink('Season', href='/season')),
                        dbc.NavItem(dbc.NavLink('Portfolio', href='/portfolio')),
                        dbc.NavItem(dbc.NavLink('Config', href='/config')),
                    ],
                    brand_href='/',
                ),
            ),
            dbc.Col(
                ThemeSwitchAIO(aio_id='theme',
                               themes=[dbc.themes.MINTY, dbc.themes.CYBORG],
                               switch_props={'value': False}),
                width='auto'),

            dbc.Col(
                navigation_page_update.get_daily_update_button(),
                width='auto',
            ),
            dcc.Store(id=nav_ids.trigger_daily),
            html.Div(id='progress-daily'),
            html.Div(id='progress-season'),
            dcc.Interval(id='interval-global', interval=1000),
        ]),
)

layout = html.Div([
    dcc.Store(id='theme-store', storage_type='session'),
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[]),
])


@app.callback(Output('theme-store', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_theme(toggle):
    return config.light_theme if toggle else config.dark_theme


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              Input('url', 'search'),
              Input('url', 'hash'))
def display_page(pathname, search, search_hash):
    if pathname == '/':
        return main_page.layout
    if pathname == '/losing':
        return losing_page.layout
    if pathname == '/card':
        if search and search_hash:
            card_page_filter.load_with_card_id = search.split('=')[-1]
            card_page_filter.load_with_account_name = search_hash.split('=')[-1]
        return card_page.layout
    if pathname == '/rating':
        return rating_page.layout
    if pathname == '/nemesis':
        return nemesis_page.layout
    if pathname == '/season':
        return season_page.layout
    if pathname == '/portfolio':
        return portfolio_page.layout
    if pathname == '/config':
        return config_page.layout
    else:  # if redirected to unknown link
        return '404 Page Error! Please choose a link'


@app.callback(Output('progress-daily', 'children'),
              Output('progress-season', 'children'),
              Trigger('interval-global', 'n_intervals'))
def update_progress():
    ret_val_daily = determine_notification(daily=True)
    ret_val_season = determine_notification()

    return ret_val_daily, ret_val_season


def determine_notification(daily=False):
    if daily:
        notification_id = 'notification-daily'
        value = progress.progress_daily_txt
        title = progress.progress_daily_title
        first = progress.progress_daily_first
    else:
        notification_id = 'notification-season'
        value = progress.progress_season_txt
        title = progress.progress_season_title
        first = progress.progress_season_first

    if not value:
        return None

    if first:
        action = 'show'
    else:
        action = 'update'
    if value == 'Done':
        if daily:
            progress.progress_daily_txt = None
        else:
            progress.progress_season_txt = None
        if daily:
            progress.progress_daily_first = True
        else:
            progress.progress_season_first = True

        return dmc.Notification(
            id=notification_id,
            title=str(title),
            message=str(value),
            color='green',
            action=action,
            autoClose=True,
            icon=DashIconify(icon='akar-icons:circle-check'),
        )
    elif value.startswith('ERROR'):
        if daily:
            progress.progress_daily_txt = None
        else:
            progress.progress_season_txt = None
        if daily:
            progress.progress_daily_first = True
        else:
            progress.progress_season_first = True

        return dmc.Notification(
            id=notification_id,
            title=str(title),
            message=str(value),
            color='red',
            action=action,
            autoClose=False,
            icon=DashIconify(icon='akar-icons:circle-x'),
        )
    else:
        if first:
            if daily:
                progress.progress_daily_first = False
            else:
                progress.progress_season_first = False

        return dmc.Notification(
            id=notification_id,
            title=str(title),
            message=str(value),
            loading=True,
            color='orange',
            action=action,
            autoClose=False,
            disallowClose=True,
        )
