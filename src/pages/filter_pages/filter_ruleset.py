import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.utils import spl_util
from src.utils.trace_logging import measure_duration

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Rule sets'),
        dcc.Dropdown(options=spl_util.get_rule_sets_list(),
                     id=filter_ids.filter_rule_sets_dropdown,
                     multi=True,
                     className='dbc',
                     style={'width': '70%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input(filter_ids.filter_rule_sets_dropdown, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_ruleset(rule_sets, filter_settings):
    filter_settings['rule_sets'] = rule_sets
    return filter_settings
