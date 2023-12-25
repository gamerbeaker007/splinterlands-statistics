import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, ctx, State

from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration
from src.pages.filter_pages import filter_style, filter_ids

from src.static.static_values_enum import Element
from src.utils import store_util


layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Rule sets'),
        dcc.Dropdown(options=store_util.get_rule_sets_list(),
                     id='dropdown-rule-sets-selection',
                     multi=True,
                     className='dbc',
                     style={'width': '70%'},
                     ),

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Input('dropdown-rule-sets-selection', 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_ruleset(rule_sets, filter_settings):
    filter_settings['rule_sets'] = rule_sets
    return filter_settings
