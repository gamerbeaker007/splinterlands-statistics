import logging
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
                    html.P('This deposit or removes an investment on a certain date'),
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
                    dbc.Input(id='amount', type='number', pattern='[0-9]'),
                    html.Div([
                        dbc.Button('Deposit', id='deposit', className='ml-auto'),
                        dbc.Button('Withdraw', id='withdraw', className='ml-auto')]
                    ),
                    html.Div([
                        html.P(id='error-text')
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
            dcc.Graph(id='total-all-portfolio-graph'),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='all-portfolio-graph'),
        ),
    ]),

    dcc.Store(id='combined-users'),
    dcc.Store(id='filtered-portfolio-df'),
    dcc.Store(id='trigger-portfolio-update')
])



@app.callback(Output('filtered-portfolio-df', 'data'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input('trigger-portfolio-update', 'data'),
              Input('trigger-daily-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_filter_data(combine_users, trigger_portfolio, trigger_daily, toggle):
    filtered_users = []
    for user in combine_users:
        if not store.portfolio.loc[(store.portfolio.account_name == user)].empty:
            filtered_users.append(user)

    store.view_portfolio_accounts = pd.DataFrame({'account_name': filtered_users})
    store_util.save_stores()

    if filtered_users:
        portfolio_df = store.portfolio.copy()
        portfolio_df = portfolio_df.loc[portfolio_df.account_name.isin(filtered_users)]
        portfolio_df = portfolio_df.groupby(['date'], as_index=False).sum()

        portfolio_df.date = pd.to_datetime(portfolio_df.date)

        # remove all other columns than value columns and date
        temp = portfolio_df.filter(regex='date|value')
        # remove all list_value's keep market_value's columns to determine total value
        portfolio_df['total_value'] = temp.filter(regex='.*(?<!_list_value)$').sum(axis=1, numeric_only=True)

        investment_df = store.portfolio_investments
        if not investment_df.empty:
            investment_df = store.portfolio_investments.copy()
            investment_df = investment_df.loc[investment_df.account_name.isin(filtered_users)]
            investment_df = investment_df.groupby(['date'], as_index=False).sum()
            investment_df.date = pd.to_datetime(investment_df.date)
            investment_df.sort_values('date', inplace=True)
            investment_df['total_sum_value'] = investment_df.sum(axis=1, numeric_only=True)
            investment_df['total_investment_value'] = investment_df.total_sum_value.cumsum()
            portfolio_df = portfolio_df.merge(investment_df[['date', 'total_investment_value']], on='date', how='outer')
        portfolio_df.sort_values('date', inplace=True)
        return portfolio_df.to_json(date_format='iso', orient='split')
    else:
        return pd.DataFrame().to_json(date_format='iso', orient='split')


@app.callback(Output('total-all-portfolio-graph', 'figure'),
              Input('filtered-portfolio-df', 'data'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(filtered_df, combine_users, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(filtered_df, orient='split')

    if temp_df.empty or len(combine_users) == 0:
        return chart_util.blank_fig(theme)
    else:
        return portfolio_graph.plot_portfolio_total(temp_df, combine_users, theme)


@app.callback(Output('all-portfolio-graph', 'figure'),
              Input('filtered-portfolio-df', 'data'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(filtered_df, combine_users, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme

    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(filtered_df, orient='split')

    if temp_df.empty or len(combine_users) == 0:
        return chart_util.blank_fig(theme)
    else:
        return portfolio_graph.plot_portfolio_all(temp_df, theme)


@app.callback(
    Output('trigger-portfolio-update', 'data'),
    [Input('deposit', 'n_clicks'),
     Input('dropdown-user-selection', 'value'),
     Input('my-date-picker-single', 'date'),
     Input('amount', 'value')],
)
def deposit_action(deposit_clicks, account, my_date, amount):
    if ctx.triggered_id == 'deposit':
        portfolio_util.update_investment(account, amount, my_date)
        logging.info('Deposit: ' + str(my_date) + ' amount: ' + str(amount))
        return True
    return False


@app.callback(
    Output('trigger-portfolio-update', 'data'),
    [Input('withdraw', 'n_clicks'),
     Input('dropdown-user-selection', 'value'),
     Input('my-date-picker-single', 'date'),
     Input('amount', 'value')],
)
def withdraw_action(withdraw_clicks, account, my_date, amount):
    if ctx.triggered_id == 'withdraw':
        portfolio_util.update_investment(account, amount*-1, my_date)
        logging.info('Withdraw: ' + str(my_date) + ' amount: ' + str(amount))
        return True
    return False


@app.callback(
    Output('error-text', 'children'),
    Output('deposit', 'disabled'),
    Output('withdraw', 'disabled'),
    Input('amount', 'value')
)
def validate_buttons(value):
    if not value:
        return '', True, True
    elif str(value).__contains__('-'):
        return 'Error do not use '-'', True, True
    else:
        return '', False, False
