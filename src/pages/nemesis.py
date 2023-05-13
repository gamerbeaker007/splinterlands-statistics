# Import necessary libraries

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback

from src import analyse
from src.configuration import config

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        html.Center(html.H1("Nemesis")),
        dbc.Col(dcc.Dropdown(options=config.account_names,
                             value=config.account_names[0],
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        html.Hr(),
        html.Br(),
        html.P('Your nemesis:'),
        html.Div(id='nemesis'),
        html.Hr(),
    ])
])


@callback(
    Output('nemesis', 'children'),
    Input('dropdown-user-selection', 'value'),
)
def nemesis(account):
    df = analyse.get_top_3_losing_account(account)

    return html.Div(children=[
        html.Ul(children=[
            html.Li(str(df.iloc[0].opponent) + " (" + str(df.iloc[0].battle_id) + ")"),
            html.Li(str(df.iloc[1].opponent) + " (" + str(df.iloc[1].battle_id) + ")"),
            html.Li(str(df.iloc[2].opponent) + " (" + str(df.iloc[2].battle_id) + ")"),
        ])
    ])
