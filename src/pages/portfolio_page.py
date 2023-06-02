import dash_bootstrap_components as dbc
from aio import ThemeSwitchAIO
from dash import html, Output, Input, dcc

from main import app
from src.configuration import config, store
from src.graphs import portfolio_graph
from src.utils import chart_util

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="total-all-portfolio-graph"),
        ),
    ]),

    html.Div(id='hidden-div-balance'),

])


@app.callback(Output('total-all-portfolio-graph', 'figure'),
              # Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.portfolio.empty:
        return chart_util.blank_fig(theme)
    else:

        return portfolio_graph.plot_portfolio_all(store.portfolio.copy(),
                                                  theme)
