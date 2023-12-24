import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from main import app, measure_duration
from src.pages.filter_pages import filter_ids
from src.pages.navigation_pages import nav_ids
from src.utils import store_util

filter_settings_lock = threading.Lock()

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Account'),
        dcc.Dropdown(id='dropdown-user-selection',
                     className='dbc',
                     style={'width': '70%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input('dropdown-user-selection', 'value'),
    Input(nav_ids.trigger_daily, 'data'),
    State(filter_ids.filter_settings, 'data'),
)
@measure_duration
def update_filter_user(account,
                       trigger_daily,
                       filter_settings,
                       ):
    # Acquire the lock before updating the shared resource
    with filter_settings_lock:
        filter_settings['account'] = account
        return filter_settings


@app.callback(
    Output('dropdown-user-selection', 'value'),
    Output('dropdown-user-selection', 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_first_account_name(), store_util.get_account_names()
