import logging
from datetime import date

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, ctx
from dash.exceptions import PreventUpdate

from main import app
from src.configuration import config
from src.pages.navigation_pages import nav_ids
from src.pages.portfolio_pages import portfolio_ids
from src.utils import store_util, portfolio_util
from src.utils.trace_logging import measure_duration


def get_div_style():
    if config.read_only:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def get_readonly_text():
    if config.read_only:
        return html.H4("Read only mode not possible to deposit/withdraw investment", className='text-warning')
    return ""


def get_deposit_layout():
    return dbc.Accordion(
        dbc.AccordionItem(
            [
                html.P('This deposit or removes an investment on a certain date'),
                html.Div(style=get_div_style(),
                         children=[
                             dbc.InputGroup(
                                 [
                                     dbc.InputGroupText('Date'),
                                     dcc.DatePickerSingle(
                                         id=portfolio_ids.data_picker,
                                         min_date_allowed=date(2015, 8, 5),
                                         initial_visible_month=date.today(),
                                         date=date.today(),
                                         className='dbc',
                                     ),
                                 ], className='mb-3'),
                             dbc.InputGroup(
                                 [
                                     dbc.InputGroupText('Account'),
                                     dcc.Dropdown(id=portfolio_ids.dropdown_user_selection_deposit,
                                                  style={'min-width': '300px'},
                                                  className='dbc'),
                                 ], className='mb-3', ),
                             dbc.InputGroup(
                                 [
                                     dbc.InputGroupText(portfolio_ids.amount),
                                     dbc.Input(id=portfolio_ids.amount, type='number', pattern='[0-9]'),
                                 ], className='mb-3'),
                             dbc.Row(
                                 [
                                     dbc.Col(dbc.Button(portfolio_ids.deposit, id=portfolio_ids.deposit,
                                                        className='ml-auto'),
                                             width=2,
                                             className='mb-3'),
                                     dbc.Col(dbc.Button(portfolio_ids.withdraw, id=portfolio_ids.withdraw,
                                                        className='ml-auto'),
                                             width=2,
                                             className='mb-3')
                                 ]),
                             html.Div([
                                 html.P(id=portfolio_ids.error_text)
                             ])
                         ]),
                html.Div(children=get_readonly_text()),
                html.Div(id=portfolio_ids.deposit_withdraw_text),
            ],
            title='deposit/withdraw investment',
        ),
        start_collapsed=True,
    ),


@app.callback(
    Output(portfolio_ids.dropdown_user_selection_deposit, 'value'),
    Output(portfolio_ids.dropdown_user_selection_deposit, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_first_account_name(), store_util.get_account_names()


@app.callback(
    Output(portfolio_ids.trigger_portfolio_update, 'data'),
    Output(portfolio_ids.deposit_withdraw_text, 'children'),
    [Input(portfolio_ids.deposit, 'n_clicks'),
     Input(portfolio_ids.dropdown_user_selection_deposit, 'value'),
     Input(portfolio_ids.data_picker, 'date'),
     Input(portfolio_ids.amount, 'value')],
)
@measure_duration
def deposit_action(deposit_clicks, account, my_date, amount):
    updated = False
    if ctx.triggered_id == portfolio_ids.deposit and account:
        if not config.read_only:
            portfolio_util.update_investment(account, amount, my_date)
            logging.info('Deposit: ' + str(my_date) + ' amount: ' + str(amount))
            text = 'Deposit processed'
            class_name = 'text-success'
            updated = True
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'
    else:
        raise PreventUpdate

    return updated, html.Div(text, className=class_name)


@app.callback(
    Output(portfolio_ids.trigger_portfolio_update, 'data'),
    Output(portfolio_ids.deposit_withdraw_text, 'children'),
    [Input(portfolio_ids.withdraw, 'n_clicks'),
     Input(portfolio_ids.dropdown_user_selection_deposit, 'value'),
     Input(portfolio_ids.data_picker, 'date'),
     Input(portfolio_ids.amount, 'value')],
)
@measure_duration
def withdraw_action(withdraw_clicks, account, my_date, amount):
    text = ''
    updated = False
    class_name = 'text-warning'
    if ctx.triggered_id == portfolio_ids.withdraw and account:
        if not config.read_only:
            portfolio_util.update_investment(account, amount * -1, my_date)
            logging.info('Withdraw: ' + str(my_date) + ' amount: ' + str(amount))
            text = 'Withdraw processed'
            class_name = 'text-success'
            updated = True
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'
    else:
        raise PreventUpdate

    return updated, html.Div(text, className=class_name)


@app.callback(
    Output(portfolio_ids.error_text, 'children'),
    Output(portfolio_ids.deposit, 'disabled'),
    Output(portfolio_ids.withdraw, 'disabled'),
    Input(portfolio_ids.amount, 'value')
)
@measure_duration
def validate_buttons(value):
    if not value:
        return '', True, True
    elif str(value).__contains__('-'):
        return html.Div("Only positive numbers are allowed", className='text-warning'), True, True
    else:
        return '', False, False
