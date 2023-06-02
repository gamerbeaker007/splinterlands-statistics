import dash_bootstrap_components as dbc
import pandas as pd
from aio import ThemeSwitchAIO
from dash import html, Output, Input, dcc

from main import app
from src.configuration import config, store
from src.graphs import portfolio_graph
from src.utils import chart_util, store_util

layout = dbc.Container([
    dbc.Row([
        dcc.Dropdown(options=store_util.get_account_names(),
                     value=store_util.get_last_portfolio_selection(),
                     multi=True,
                     id='dropdown-user-selection-portfolio',
                     className='dbc',
                     ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="total-all-portfolio-graph"),
        ),
    ]),

    html.Div(id='hidden-div-balance'),

])


@app.callback(Output('total-all-portfolio-graph', 'figure'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(combine_users, toggle):

    store.view_portfolio_accounts = pd.DataFrame({'account_name': combine_users})
    store_util.save_stores()

    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.portfolio.empty or len(combine_users) == 0:
        return chart_util.blank_fig(theme)
    else:

        df = store.portfolio.copy()
        df = df.loc[df.account_name.isin(combine_users)]
        return portfolio_graph.plot_portfolio_total(df,
                                                    theme)
