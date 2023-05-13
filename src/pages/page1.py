# Import necessary libraries
import dash_bootstrap_components as dbc
from aio import ThemeSwitchAIO
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
        dcc.Graph(id="modern-rating-graph"),
        dcc.Graph(id="wild-rating-graph"),
    ]),
])


@callback(Output('modern-rating-graph', 'figure'),
          Input('dropdown-user-selection', 'value'),
          Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
          )
def update_modern_graph(account, toggle):
    # TODO check which order callbacks are done
    config.theme = 'minty' if toggle else 'cyborg'

    df = get_rating_df(account, Format.MODERN.value)
    fig = px.line(df, x='created_date', y='rating', color='account', template=config.theme)
    return fig


@callback(Output('wild-rating-graph', 'figure'),
          Input('dropdown-user-selection', 'value'),
          Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
          )
def update_wild_graph(account, toggle):
    # TODO check which order callbacks are done
    config.theme = 'minty' if toggle else 'cyborg'

    df = get_rating_df(account, Format.WILD.value)
    fig = px.line(df, x='created_date', y='rating', color='account', template=config.theme)
    return fig


def get_rating_df(account, match_format):
    if account == 'ALL':
        df = store.rating_df
    else:
        df = store.rating_df.loc[(store.rating_df.account == account)]

    df = df.loc[(store.rating_df.format == match_format)]
    df.sort_values(by='created_date', inplace=True)
    return df
