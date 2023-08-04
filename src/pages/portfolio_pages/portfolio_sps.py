import pandas as pd
from dash import Output, Input, dcc

from src.pages.main_dash import app
from src.utils import chart_util


def get_sps_layout():
    return dcc.Graph(id='portfolio-sps-graph')


@app.callback(Output('portfolio-sps-graph', 'figure'),
              Input('filtered-portfolio-df', 'data'),
              Input('theme-store', 'data'),
              )
def update_portfolio_editions_graph(filtered_df, theme):

    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        portfolio_df = pd.read_json(filtered_df, orient='split')

    if portfolio_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return chart_util.blank_fig(theme)

        # portfolio_df.sort_values(by='date', inplace=True)
        # editions_df = portfolio_df.loc[:,
        #               portfolio_df.columns.str.startswith('date') |
        #               (portfolio_df.columns.str.startswith('sps') &
        #                (portfolio_df.columns.str.endswith("market_value") | portfolio_df.columns.str.endswith(
        #                    "_bcx"))
        #                )]
        #
        # # drop empty rows
        # editions_df = editions_df.set_index('date').dropna(how='all')
        #
        # # drop columns that have a sum of 0 bxc and market_value
        # for edition in Edition.list_names():
        #     if (editions_df[str(edition) + "_market_value"] + editions_df[str(edition) + "_bcx"]).sum() == 0:
        #         # drop columns that have a sum of 0
        #         editions_df.drop(columns=str(edition) + "_market_value", inplace=True)
        #         editions_df.drop(columns=str(edition) + "_bcx", inplace=True)
        #
        # return portfolio_graph.get_editions_fig(editions_df, theme)
