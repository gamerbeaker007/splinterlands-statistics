# Import necessary libraries
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, callback, Input
import plotly.express as px

from src.configuration import config, store
from src.static.static_values_enum import Format

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        html.Center(html.H1("Page 1")),
        dbc.Col(dcc.Dropdown(options=['ALL'] + config.account_names,
                             value='ALL',
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        html.Br(),
        html.Hr(),
        dbc.Col([
            html.P("This is column 1."),
            dbc.Button("Test Button", color="primary")
        ]),
        dbc.Col([
            html.P("This is column 2."),
            html.P("You can add many cool components using the bootstrap dash components library."),
        ]),
        dcc.Graph(id="chart"),
    ]),
])


@callback(Output('chart', 'figure'),
          Input('dropdown-user-selection', 'value'),
          )
def update_figure(value):
    if value == 'ALL':
        df = store.rating_df
    else:
        df = store.rating_df.loc[(store.rating_df.account == value)]

    df = df.loc[(store.rating_df.format == Format.MODERN.value)]
    df.sort_values(by='created_date', inplace=True)
    fig = px.line(df, x='created_date', y='rating', color='account', template='darkly')
    return fig
