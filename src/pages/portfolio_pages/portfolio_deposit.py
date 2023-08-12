import logging
from datetime import date
from main import app

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, ctx

from src.utils import store_util, portfolio_util


def get_deposit_layout():
    return dbc.Accordion(
        dbc.AccordionItem(
            [
                html.P('This deposit or removes an investment on a certain date'),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('Date'),
                        dcc.DatePickerSingle(
                            id='my-date-picker-single',
                            min_date_allowed=date(2015, 8, 5),
                            initial_visible_month=date.today(),
                            date=date.today(),
                            className='dbc',
                        ),
                    ], className='mb-3'),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('Account'),
                        dcc.Dropdown(options=store_util.get_account_names(),
                                     value=store_util.get_first_account_name(),
                                     id='dropdown-user-selection',
                                     style={'min-width': '300px'},
                                     className='dbc'),
                    ], className='mb-3', ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('Amount'),
                        dbc.Input(id='amount', type='number', pattern='[0-9]'),
                    ], className='mb-3'),
                dbc.Row(
                    [
                        dbc.Col(dbc.Button('Deposit', id='deposit', className='ml-auto'),
                                width=2,
                                className='mb-3'),
                        dbc.Col(dbc.Button('Withdraw', id='withdraw', className='ml-auto'),
                                width=2,
                                className='mb-3')
                    ]),
                html.Div([
                    html.P(id='error-text')
                ])
            ],
            title='deposit/withdraw investment',
        ),
        start_collapsed=True,
    ),

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
        portfolio_util.update_investment(account, amount * -1, my_date)
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
        return html.Div("Only positive numbers are allowed", className='text-warning'), True, True
    else:
        return '', False, False
