import logging

import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx

from main import app
from src import balances_info
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


@app.callback(
    Output('hidden-div-balance', 'children'),
    Input('update-season-btn', 'n_clicks'),
)
def update_output(n_clicks):
    if "update-season-btn" == ctx.triggered_id:
        logging.info("Update season button was clicked")
        balances_info.get_balances()
        store_util.save_stores()


