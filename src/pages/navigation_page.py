import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import html, Output, Input, dcc, ctx
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import ThemeSwitchAIO
from dash_extensions.enrich import Trigger
from dash_iconify import DashIconify

from main import app
from src import battle_store, collection_store, portfolio
from src.configuration import progress
from src.pages import main_page, rating_page, nemesis_page, losing_page, season_page, config_page, portfolio_page
from src.utils import store_util, progress_util

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
                dbc.Button(
                    'Update daily',
                    id='load-new-values',
                    color='primary',
                    className='ms-2', n_clicks=0
                ),
                width='auto',
            ),
            dcc.Store(id='trigger-daily-update'),
            html.Div(id='progress-daily'),
            html.Div(id='progress-season'),
            dcc.Interval(id='interval-global', interval=1000),
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
    if pathname == '/season':
        return season_page.layout
    if pathname == '/portfolio':
        return portfolio_page.layout
    if pathname == '/config':
        return config_page.layout
    else:  # if redirected to unknown link
        return '404 Page Error! Please choose a link'


@app.callback(
    Output('trigger-daily-update', 'data'),
    Input('load-new-values', 'n_clicks'),
)
def update__output(n_clicks):
    if 'load-new-values' == ctx.triggered_id:
        progress_util.set_daily_title('Update collection')
        collection_store.update_collection()

        progress_util.set_daily_title('Update battles')
        battle_store.process_battles()

        progress_util.set_daily_title('Update portfolio')
        portfolio.update_portfolios()

        store_util.save_stores()
        progress_util.update_daily_msg('Done')
        return True
    return False


@app.callback(Output('progress-daily', 'children'),
              Output('progress-season', 'children'),
              Trigger('interval-global', 'n_intervals'))
def update_progress(interval):
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
