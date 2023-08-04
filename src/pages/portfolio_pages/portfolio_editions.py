import pandas as pd
from aio import ThemeSwitchAIO
from dash import Output, Input, html, dcc

from src.configuration import config
from src.pages.main_dash import app
from src.utils import chart_util
import dash_bootstrap_components as dbc


def get_edition_layout():
    return dcc.Graph(id='portfolio-editions-graph')


@app.callback(Output('portfolio-editions-graph', 'figure'),
              Input('filtered-portfolio-df', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_portfolio_editions_graph(filtered_df, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(filtered_df, orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        # TODO
        return chart_util.blank_fig(theme)
