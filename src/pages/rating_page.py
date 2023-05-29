import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
from dash_bootstrap_templates import ThemeSwitchAIO

from main import app
from src.configuration import config, store
from src.graphs import rating_graph
from src.static.static_values_enum import Format
from src.utils import store_util, chart_util

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=['ALL'] + store_util.get_account_names(),
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


@app.callback(Output('modern-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    df = get_rating_df(account, Format.MODERN.value)
    if df.empty:
        return chart_util.blank_fig(theme)
    else:
        return rating_graph.create_rating_graph(df, theme)


@app.callback(Output('wild-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    df = get_rating_df(account, Format.WILD.value)
    if df.empty:
        return chart_util.blank_fig(theme)
    else:
        return rating_graph.create_rating_graph(df, theme)


def get_rating_df(account, match_format):
    if account == 'ALL':
        df = store.rating
    else:
        df = store.rating.loc[(store.rating.account == account)]

    if df.empty:
        return df
    else:
        df = df.loc[(store.rating.format == match_format)].copy()
        df.sort_values(by='created_date', inplace=True)
        return df
