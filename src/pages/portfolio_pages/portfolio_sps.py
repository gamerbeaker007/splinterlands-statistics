from io import StringIO

import pandas as pd
from dash import Output, Input, dcc

from src.graphs import portfolio_graph
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.portfolio_pages import portfolio_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration


def get_sps_layout():
    return dcc.Graph(id=portfolio_ids.portfolio_sps_graph)


@app.callback(
    Output(portfolio_ids.portfolio_sps_graph, 'figure'),
    Input(portfolio_ids.filtered_portfolio_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_portfolio_sps_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        portfolio_df = pd.read_json(StringIO(filtered_df), orient='split')

    if portfolio_df.empty:
        return chart_util.blank_fig(theme)
    else:
        portfolio_df.sort_values(by='date', inplace=True)
        sps_df = portfolio_df.loc[:,
                 portfolio_df.columns.str.startswith('date') |
                 portfolio_df.columns.str.startswith('sps')]

        # drop empty rows
        sps_df = sps_df.set_index('date').dropna(how='all')
        sps_df = sps_df.loc[(sps_df.sum(axis=1) != 0)]

        return portfolio_graph.get_sps_fig(sps_df, theme)
