import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from main import app, measure_duration
from src.pages.filter_pages import filter_ids

filter_settings_lock = threading.Lock()

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Group levels'),
        dcc.RadioItems(options=['True', 'False'],
                       value='True',
                       inline=True,
                       id='radio-by-selection',
                       className='mt-2 dbc',
                       labelStyle={'marginLeft': '10px', 'display': 'inline-block'}
                       ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input('radio-by-selection', 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def set_group_levels(value, filter_settings):
    # Acquire the lock before updating the shared resource
    with filter_settings_lock:
        if value == 'True':
            filter_settings['group_levels'] = True
        else:
            filter_settings['group_levels'] = False
        return filter_settings
