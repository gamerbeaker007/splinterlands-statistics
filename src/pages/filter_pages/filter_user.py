import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import store_util
from src.utils.trace_logging import measure_duration

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Account'),
        dcc.Dropdown(id=filter_ids.filter_user_dropdown,
                     className='dbc',
                     style={'width': '70%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input(filter_ids.filter_user_dropdown, 'value'),
    Input(nav_ids.trigger_daily, 'data'),
    State(filter_ids.filter_settings, 'data'),
)
@measure_duration
def update_filter_user(account,
                       trigger_daily,
                       filter_settings,
                       ):
    filter_settings['account'] = account
    return filter_settings


@app.callback(
    Output(filter_ids.filter_user_dropdown, 'value'),
    Output(filter_ids.filter_user_dropdown, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_first_account_name(), store_util.get_account_names()
