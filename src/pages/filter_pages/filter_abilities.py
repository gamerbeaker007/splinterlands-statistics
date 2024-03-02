import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.utils import spl_util
from src.utils.trace_logging import measure_duration

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Ability'),
        dcc.Dropdown(options=spl_util.get_ability_list(),
                     id=filter_ids.filter_abilities_dropdown,
                     multi=True,
                     className='dbc',
                     style={'width': '70%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input(filter_ids.filter_abilities_dropdown, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_abilities(ability, filter_settings):
    filter_settings['abilities'] = ability
    return filter_settings
