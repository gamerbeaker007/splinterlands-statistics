import logging

from dash import html, callback, Output, Input, dash_table, dcc, ctx
import dash_bootstrap_components as dbc
from src import analyse, balances_info
from src.configuration import config
from src.static import static_values_enum
from src.static.static_values_enum import MatchType, CardType
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Update press button'),
        dbc.Col(
            dbc.Button(
                'Pull new data',
                id='update-season-btn',
                color='primary',
                className='ms-2', n_clicks=0
            ),
            width='auto',
        ),

    ]),
    html.Div(id='hidden-div-balance', style={'display': 'none'}),
])


@callback(
    Output('hidden-div-balance', 'children'),
    Input('update-season-btn', 'n_clicks'),
)
def update_output(n_clicks):
    if "update-season-btn" == ctx.triggered_id:
        logging.info("Update season button was clicked")
        balances_info.get_balances()
        store_util.save_stores()


