import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Group levels'),
        dcc.RadioItems(options=['True', 'False'],
                       value='True',
                       inline=True,
                       id=filter_ids.filter_group_levels_radio_selection,
                       className='mt-2 dbc',
                       labelStyle={'marginLeft': '10px', 'display': 'inline-block'}
                       ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input(filter_ids.filter_group_levels_radio_selection, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def set_group_levels(value, filter_settings):
    if value == 'True':
        filter_settings['group_levels'] = True
    else:
        filter_settings['group_levels'] = False
    return filter_settings
