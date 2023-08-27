import dash_bootstrap_components as dbc
from dash import dcc, Output, Input, ctx
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Trigger

from main import app
from src import battle_store, collection_store, portfolio
from src.configuration import config
from src.pages.navigation_pages import nav_ids
from src.utils import progress_util, store_util

SERVER_MODE_INTERVAL_IN_MINUTES = 90


def get_daily_update_button():
    if config.server_mode:
        return dcc.Interval(id=nav_ids.server_mode_interval, interval=SERVER_MODE_INTERVAL_IN_MINUTES * 60 * 1000),
    else:
        return dbc.Button(
            'Update daily',
            id=nav_ids.load_new_values,
            color='primary',
        ),


def update_data():
    progress_util.set_daily_title('Update collection')
    collection_store.update_collection()

    progress_util.set_daily_title('Update battles')
    battle_store.process_battles()

    progress_util.set_daily_title('Update portfolio')
    portfolio.update_portfolios()

    store_util.save_stores()
    progress_util.update_daily_msg('Done')


if config.server_mode:
    @app.callback(
        Output(nav_ids.trigger_daily, 'data'),
        Trigger(nav_ids.server_mode_interval, 'n_intervals'),
    )
    def update_server_mode_interval():
        update_data()
        return True
else:
    @app.callback(
        Output(nav_ids.trigger_daily, 'data'),
        Input(nav_ids.load_new_values, 'n_clicks'),
    )
    def update_daily_button(n_clicks):
        if ctx.triggered_id == nav_ids.load_new_values:
            update_data()
            return True
        else:
            raise PreventUpdate
