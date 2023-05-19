# Import necessary libraries
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import ThemeSwitchAIO
from dash import html, dcc, Output, callback, Input

from src.configuration import config, store
from src.static.static_values_enum import Format

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=['ALL'] + config.account_names,
                             value='ALL',
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        html.Center(html.H1("Modern")),
        html.Br(),
        html.Hr(),
        dcc.Graph(id="modern-rating-graph"),
        html.Center(html.H1("Wild")),
        dcc.Graph(id="wild-rating-graph"),
    ]),
])


@callback(Output('modern-rating-graph', 'figure'),
          Input('dropdown-user-selection', 'value'),
          Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
          )
def update_modern_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    df = get_rating_df(account, Format.MODERN.value)
    fig = px.scatter(df, x='created_date', y='rating', color='account', template=theme)
    return fig


@callback(Output('wild-rating-graph', 'figure'),
          Input('dropdown-user-selection', 'value'),
          Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
          )
def update_wild_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    df = get_rating_df(account, Format.WILD.value)
    fig = px.scatter(df, x='created_date', y='rating', color='account', template=theme)
    return fig


def get_rating_df(account, match_format):
    if account == 'ALL':
        df = store.rating_df
    else:
        df = store.rating_df.loc[(store.rating_df.account == account)]

    df = df.loc[(store.rating_df.format == match_format)]
    df.sort_values(by='created_date', inplace=True)
    return df
