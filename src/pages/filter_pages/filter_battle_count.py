import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, State

from main import app, measure_duration
from src.pages.filter_pages import filter_ids

filter_settings_lock = threading.Lock()

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Minimal battles'),
        dbc.Input(id='minimal-battles-filter',
                  min=0,
                  value=0,
                  type='number',
                  pattern='[0-9]')
    ],
    className='mb-3',
)


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input('minimal-battles-filter', 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def update_minimal_battle_filter(value, filter_settings):
    # Acquire the lock before updating the shared resource
    with filter_settings_lock:
        if not value:
            value = 0
        filter_settings['minimal-battles'] = value
        return filter_settings
