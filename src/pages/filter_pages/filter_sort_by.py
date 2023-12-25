import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration
from src.pages.filter_pages import filter_ids


layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Sort by'),
        dcc.Dropdown(options=['battles', 'percentage', 'win', 'loss'],
                     value=['battles'],
                     id='dropdown-sort-by-selection',
                     multi=True,
                     className='dbc',
                     style={'width': '50%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input('dropdown-sort-by-selection', 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def sort_by(sorts, filter_settings):
    filter_settings['sort_by'] = sorts
    return filter_settings
