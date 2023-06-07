from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
from aio import ThemeSwitchAIO
from dash import html, Output, Input, dcc, ctx

from main import app
from src.configuration import config, store
from src.graphs import portfolio_graph
from src.utils import chart_util, store_util, portfolio_util

layout = dbc.Container([
    dbc.Row([
        dbc.Accordion(
            dbc.AccordionItem(
                [
                    html.P("This add or removes an investment on a certain date"),
                    dcc.DatePickerSingle(
                        id='my-date-picker-single',
                        min_date_allowed=date(2015, 8, 5),
                        initial_visible_month=date.today(),
                        date=date.today(),
                        className='dbc',
                    ),
                    dbc.Col(dcc.Dropdown(options=store_util.get_account_names(),
                                         value=store_util.get_first_account_name(),
                                         id='dropdown-user-selection',
                                         className='dbc'),
                            ),
                    dbc.Input(id='amount', type='number', pattern="[0-9]"),
                    html.Div([
                        dbc.Button("Add", id="add", className="ml-auto"),
                        dbc.Button("Withdraw", id="withdraw", className="ml-auto")]
                    ),
                    html.Div([
                        html.P(id="error-text")
                    ])
                ],
                title='deposit/withdraw investment',
            ),
            start_collapsed=True,
        )

    ]),
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
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="all-portfolio-graph"),
        ),
    ]),

    html.Div(id='hidden-div-portfolio'),

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

        portfolio_df = store.portfolio.copy()
        portfolio_df = portfolio_df.loc[portfolio_df.account_name.isin(combine_users)]
        account_names = portfolio_df.account_name.unique().tolist()
        portfolio_df = portfolio_df.groupby(['date'], as_index=False).sum()
        investment_df = store.portfolio_investments
        if not investment_df.empty:
            investment_df = store.portfolio_investments.copy()
            investment_df = investment_df.loc[investment_df.account_name.isin(combine_users)]
            investment_df = investment_df.groupby(['date'], as_index=False).sum()
        return portfolio_graph.plot_portfolio_total(portfolio_df, investment_df, account_names, theme)


@app.callback(Output('all-portfolio-graph', 'figure'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(combine_users, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.portfolio.empty or store.portfolio.loc[store.portfolio.account_name.isin(combine_users)].empty:
        return chart_util.blank_fig(theme)
    else:

        df = store.portfolio.copy()
        df = df.loc[df.account_name.isin(combine_users)]
        df = df.groupby(['date'], as_index=False).sum()

        return portfolio_graph.plot_portfolio_all(df, theme)


@app.callback(
    Output("hidden-div-portfolio", "data"),
    [Input("add", "n_clicks"),
     Input("dropdown-user-selection", "value"),
     Input('my-date-picker-single', 'date'),
     Input('amount', 'value')],
)
def toggle_add(add_clicks, account, my_date, amount):
    if ctx.triggered_id == "add":
        portfolio_util.update_investment(account, amount, my_date)
        print("add: " + str(my_date) + " amount: " + str(amount))


@app.callback(
    Output("error-text", "children"),
    Output("add", "disabled"),
    Output("withdraw", "disabled"),
    Input("amount", "value")
)
def update_buttons(value):
    if not value:
        return "", True, True
    elif str(value).__contains__("-"):
        return "Error do not use '-'", True, True
    else:
        return "", False, False


@app.callback(
    Output("hidden-div-portfolio", "data"),
    [Input("withdraw", "n_clicks"),
     Input("dropdown-user-selection", "value"),
     Input('my-date-picker-single', 'date'),
     Input('amount', 'value')],
)
def toggle_withdraw(withdraw_clicks, account, my_date, amount):
    if ctx.triggered_id == "withdraw":
        portfolio_util.update_investment(account, amount*-1, my_date)
        print("withdraw: " + str(my_date) + " amount: " + str(amount))
