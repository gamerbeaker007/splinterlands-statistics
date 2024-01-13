import dash_bootstrap_components as dbc
from dash import Output, Input, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Minimal battles'),
        dbc.Input(id=filter_ids.filter_battle_count,
                  min=0,
                  value=0,
                  className='border border-dark',
                  style={'--bs-border-opacity': '0.2'},
                  type='number',
                  pattern='[0-9]')
    ],
    className='mb-3 dbc',
)


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input(filter_ids.filter_battle_count, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def update_minimal_battle_filter(value, filter_settings):
    if not value:
        value = 0
    filter_settings['minimal-battles'] = value
    return filter_settings
