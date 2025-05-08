import dash_bootstrap_components as dbc
from dash import html

layout = dbc.Container(
    [
        dbc.Row(
            children=[
                html.H3("This page is moved to the following site:"),
                html.A(
                    "https://splinter-lands.streamlit.app/",
                    href="https://splinter-lands.streamlit.app/",
                    target="_blank",
                    style={"color": "blue", "textDecoration": "underline"}
                )
            ],
            style={"fontFamily": "Arial", "padding": "50px"}),
    ]
)
