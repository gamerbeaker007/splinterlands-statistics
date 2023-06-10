import dash_bootstrap_components as dbc
import pandas as pd
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
        dcc.Store(id='filtered-rating-df')
    ]),
])


@app.callback(Output('filtered-rating-df', 'data'),
              Input('dropdown-user-selection', 'value'),
              )
def filter_rating_df(account):
    if account == 'ALL':
        df = store.rating
    else:
        df = store.rating.loc[(store.rating.account == account)]

    if not df.empty:
        df.loc[:].sort_values(by='created_date', inplace=True)

    return df.to_json(date_format='iso', orient='split')


@app.callback(Output('modern-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_graph(filtered_df, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.MODERN.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


@app.callback(Output('wild-rating-graph', 'figure'),
              Input('filtered-rating-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_graph(filtered_df, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        df = filtered_df.loc[(store.rating.format == Format.WILD.value)]
        return rating_graph.create_rating_graph(df, theme)

    return chart_util.blank_fig(theme)


