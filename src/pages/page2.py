# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import html

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        html.Center(html.H1("Page 2")),
        html.Br(),
        html.Hr(),
        dbc.Col([
            html.P("This is column 1."),
            dbc.Button("Test Button", color="primary")
        ]),
        dbc.Col([
            html.P("This is column 2."),
            html.P("You can add many cool components using the bootstrap dash components library."),
        ])
    ])
])