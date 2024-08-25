from io import StringIO

import pandas as pd
from dash import Output, Input, dcc

from src.graphs import portfolio_graph
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.portfolio_pages import portfolio_ids
from src.static.static_values_enum import Edition
from src.utils import chart_util
from src.utils.trace_logging import measure_duration


def get_edition_layout():
    return dcc.Graph(id=portfolio_ids.portfolio_editions_graph)


@app.callback(
    Output(portfolio_ids.portfolio_editions_graph, 'figure'),
    Input(portfolio_ids.filtered_portfolio_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_portfolio_editions_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        portfolio_df = pd.read_json(StringIO(filtered_df), orient='split')

    if portfolio_df.empty:
        return chart_util.blank_fig(theme)
    else:
        portfolio_df.sort_values(by='date', inplace=True)

        # filter market value and bcx columns for every edition
        date_column = portfolio_df.columns.str.startswith('date')
        columns = portfolio_df.columns.str.endswith("market_value") | portfolio_df.columns.str.endswith("_bcx")
        edition_columns = portfolio_df.columns.str.startswith(tuple(Edition.list_names()))
        editions_df = portfolio_df.loc[:, date_column | (edition_columns & columns)]

        # drop empty rows
        editions_df = editions_df.set_index('date').dropna(how='all')
        editions_df = editions_df.loc[(editions_df.sum(axis=1) != 0)]

        # drop columns that have a sum of 0 bxc and market_value
        for edition in Edition.list_names():
            if str(edition) + "_market_value" in editions_df.columns.tolist():
                if (editions_df[str(edition) + "_market_value"] + editions_df[str(edition) + "_bcx"]).sum() == 0:
                    # drop columns that have a sum of 0
                    editions_df.drop(columns=str(edition) + "_market_value", inplace=True)
                    editions_df.drop(columns=str(edition) + "_bcx", inplace=True)

        return portfolio_graph.get_editions_fig(editions_df, theme)
