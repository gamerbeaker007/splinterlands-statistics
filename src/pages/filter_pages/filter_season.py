import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration
from src.pages.filter_pages import filter_ids
from src.pages.navigation_pages import nav_ids
from src.utils import season_util

date_fmt = '%Y-%m-%d %H:%M (UTC)'

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Since season'),
        dcc.Dropdown(id='dropdown-season-selection',
                     clearable=False,
                     value=season_util.first_played_season(),
                     options=season_util.get_season_played(),
                     style={'width': '85px'},
                     className='dbc'),
        dbc.InputGroupText(id='filter-from-date',
                           children=season_util
                           .get_season_end_date(season_util.first_played_season())
                           .strftime(date_fmt))

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
    if season_id:
        from_date = season_util.get_season_end_date(season_id)

        filter_settings['from_date'] = from_date
        return filter_settings, str(from_date.strftime(date_fmt))
    else:
        return filter_settings, ''


@app.callback(
    Output('dropdown-season-selection', 'options'),
    Output('dropdown-season-selection', 'value'),
    Input(nav_ids.trigger_daily, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def update_season_callback(trigger):
    return season_util.get_season_played(), season_util.first_played_season()
