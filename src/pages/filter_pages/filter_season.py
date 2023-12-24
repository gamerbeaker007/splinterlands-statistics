import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State
from dateutil import parser

from main import app, measure_duration
from src.configuration import store
from src.pages.filter_pages import filter_ids
from src.pages.navigation_pages import nav_ids
from src.utils import store_util

filter_settings_lock = threading.Lock()

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Since season'),
        dcc.Dropdown(id='dropdown-season-selection',
                     clearable=False,
                     style={'width': '85px'},
                     className='dbc'),
        dbc.InputGroupText(id='filter-from-date')

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Output('filter-from-date', 'children'),
    Input('dropdown-season-selection', 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_season_df(season_id, filter_settings):
    # Acquire the lock before updating the shared resource
    with filter_settings_lock:
        if season_id:
            season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
            from_date = parser.parse(season_end_date)

            filter_settings['from_date'] = from_date
            return filter_settings, str(from_date.strftime('%Y-%m-%d %H:%M (UTC)'))
        else:
            return filter_settings, ''


@app.callback(
    Output('dropdown-season-selection', 'options'),
    Output('dropdown-season-selection', 'value'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_seasons_played_list(tigger):
    season_played = store_util.get_seasons_played_list()
    first_played_season = ''
    if len(season_played) > 0:
        first_played_season = season_played[-1]
    return season_played, first_played_season
