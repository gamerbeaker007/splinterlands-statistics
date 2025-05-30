import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, ctx
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_extensions.enrich import Trigger
from dash_iconify import DashIconify

from src.configuration import progress, config
from src.pages import main_page
from src.pages.card_pages import card_page, card_page_filter
from src.pages.config_pages import config_page
from src.pages.land_pages import land_page
from src.pages.land_resources_pages import land_resources_page
from src.pages.losing_pages import losing_page
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.nemesis_pages import nemesis_page
from src.pages.portfolio_pages import portfolio_page
from src.pages.rating_pages import rating_page
from src.pages.season_pages import season_page
from src.pages.shared_modules import styles
from src.utils import store_util
from src.utils.trace_logging import measure_duration

SPL_LOGO = 'https://d36mxiodymuqjm.cloudfront.net/website/icons/img_icon_splinterlands.svg'

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=SPL_LOGO, height='150px')),
                        dbc.Col(
                            dbc.NavbarBrand('SPL Battle statistics (' + config.APP_VERSION + ')', className='ms-2')),
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
                        dbc.NavItem(dbc.NavLink('Land', href='/land')),
                        dbc.NavItem(dbc.NavLink('Land R', href='/land-resources')),
                        dbc.NavItem(dbc.NavLink('Config', href='/config')),
                    ],
                    brand_href='/',
                ),
                width='auto'
            ),
            dbc.Col(
                ThemeSwitchAIO(aio_id='theme',
                               themes=[dbc.themes.MINTY, dbc.themes.CYBORG],
                               switch_props={'value': False}),
                width='auto'
            ),
            dbc.Col(
                dbc.Button(
                    'Update daily',
                    id=nav_ids.load_new_values,
                    color='primary',
                    className='m-1',
                ),
                width='auto',
                style=styles.get_server_mode_style(),
            ),
            dcc.Store(id=nav_ids.trigger_daily),
            html.Div(id=nav_ids.progress_daily),
            html.Div(id=nav_ids.progress_season),
            dcc.Interval(id=nav_ids.interval_global, interval=1000),
        ]),
)

layout = html.Div([
    dcc.Store(id=nav_ids.theme_store, storage_type='session'),
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[]),
])


@app.callback(
    Output(nav_ids.theme_store, 'data'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
@measure_duration
def update_theme(toggle):
    config.current_theme = config.light_theme if toggle else config.dark_theme
    return config.current_theme


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    Input('url', 'search'),
    Input('url', 'hash'),
)
@measure_duration
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
    if pathname == '/land':
        return land_page.layout
    if pathname == '/land-resources':
        return land_resources_page.layout
    if pathname == '/config':
        return config_page.layout
    else:  # if redirected to unknown link
        return '404 Page Error! Please choose a link'


@app.callback(
    Output(nav_ids.progress_daily, 'children'),
    Output(nav_ids.progress_season, 'children'),
    Trigger(nav_ids.interval_global, 'n_intervals'),
)
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


@app.callback(
    Output(nav_ids.trigger_daily, 'data'),
    Input(nav_ids.load_new_values, 'n_clicks'),
)
@measure_duration
def update_daily_button(n_clicks):
    if ctx.triggered_id == nav_ids.load_new_values and not config.server_mode:
        store_util.update_data(battle_update=True, season_update=False)
        return True
    else:
        raise PreventUpdate
