import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
from dash import html, dcc, Output, Input
from dash_bootstrap_templates import ThemeSwitchAIO

from main import app
from src.configuration import config, store
from src.static import static_values_enum
from src.static.static_values_enum import Format, RatingLevel
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


def create_rating_graph(df, theme):
    fig = px.scatter(df, x='created_date', y='rating', color='account', template=theme, height=800)
    # Start from 1 skip Novice
    for i in np.arange(1, len(static_values_enum.league_ratings)):
        y = static_values_enum.league_ratings[i]
        color = static_values_enum.league_colors[i]
        league_name = RatingLevel(i).name

        fig.add_hline(y=y,
                      line_width=1,
                      line_dash="dash",
                      annotation_text=league_name,
                      annotation_position="top left",
                      line_color=color)
    return fig


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
        return create_rating_graph(df, theme)


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
        return create_rating_graph(df, theme)


def get_rating_df(account, match_format):
    if account == 'ALL':
        df = store.rating_df
    else:
        df = store.rating_df.loc[(store.rating_df.account == account)]

    if df.empty:
        return df
    else:
        df = df.loc[(store.rating_df.format == match_format)].copy()
        df.sort_values(by='created_date', inplace=True)
        return df
