import logging
from datetime import date, datetime

import dash_bootstrap_components as dbc
import pandas as pd
from aio import ThemeSwitchAIO
from dash import html, Output, Input, dcc, ctx
from dash.exceptions import PreventUpdate

from main import app
from src.configuration import config, store
from src.graphs import portfolio_graph
from src.static import static_values_enum
from src.static.static_values_enum import Edition
from src.utils import chart_util, store_util, portfolio_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Portfolio'),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Combine accounts'),
                    dcc.Dropdown(multi=True,
                                 id='dropdown-user-selection-portfolio',
                                 className='dbc',
                                 style={'min-width': '350px'},
                                 ),
                ],
                className='mb-3',
            ),
        ),
        dbc.Col(
            dbc.Accordion(
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
            className='mb-3',
        ),
    ]),
    dbc.Row(id='update-values-row'),
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


@app.callback(Output('dropdown-user-selection-portfolio', 'value'),
              Output('dropdown-user-selection-portfolio', 'options'),
              Input('trigger-daily-update', 'data'),
              )
def update_user_list(tigger):
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(Output('filtered-portfolio-df', 'data'),
              Input('dropdown-user-selection-portfolio', 'value'),
              Input('trigger-portfolio-update', 'data'),
              Input('trigger-daily-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_filter_data(combine_users, trigger_portfolio, trigger_daily, toggle):
    filtered_users = []
    for user in combine_users:
        if not store.portfolio.empty and not store.portfolio.loc[(store.portfolio.account_name == user)].empty:
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
def update_portfolio_total_graph(filtered_df, combine_users, toggle):
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
def update_portfolio_all_graph(filtered_df, combine_users, toggle):
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


def create_value_card(title, text, image_url):
    return dbc.Card(
        [
            dbc.CardImg(
                src=image_url,
                top=True,
                style={"opacity": 0.3, "height": "100px", "width": "100px"},
                className="align-self-center",  # Center the image within the card
            ),
            dbc.CardImgOverlay(
                dbc.CardBody(
                    [
                        html.H6(title,
                                className="card-title",
                                style={"fontSize": 16},
                                ),
                        html.P(
                            text,
                            className="card-text",
                            style={"fontSize": 14},
                        ),
                    ],
                    className="align-items-start",  # Align CardBody to the top
                ),
                className="d-flex justify-content-center align-items-center",  # Center the overlay content
            ),
        ],
        className="mb-3",
    )


@app.callback(
    Output('update-values-row', 'children'),
    Input('filtered-portfolio-df', 'data'),
    Input('total-all-portfolio-graph', 'clickData'))
def display_click_data(filtered_portfolio_df, clickData):
    if not filtered_portfolio_df:
        raise PreventUpdate
    else:
        filtered_portfolio_df = pd.read_json(filtered_portfolio_df, orient='split')

    if clickData:
        target_date = clickData['points'][0]['x']
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')

    filtered_portfolio_df.sort_values(by='date', inplace=True)
    filtered_portfolio_df = filtered_portfolio_df[filtered_portfolio_df['date'] <= target_date]

    # Determine invested amount
    invested_value = 0
    if 'total_investment_value' in filtered_portfolio_df.columns.tolist():
        investment_df = filtered_portfolio_df.loc[(filtered_portfolio_df.total_investment_value.notna())]
        invested_value = investment_df.iloc[-1].total_investment_value

    value_df = filtered_portfolio_df.loc[(filtered_portfolio_df.total_value.notna())]
    value_row = value_df.iloc[-1]

    total_value = value_row.total_value

    # For old version there might be an collection_list_value
    if 'collection_list_value' in value_row.index.to_list() and value_row.collection_list_value > 0:
        card_list_value_columns = value_row.index[value_row.index.str.startswith('collection_list_value')]
        card_market_value_columns = value_row.index[value_row.index.str.startswith('collection_market_value')]
        card_list_value = value_row.collection_list_value
        card_market_value = value_row.collection_market_value
    else:
        card_list_value_columns = value_row.index[
            value_row.index.str.startswith(tuple(list(Edition.list_names()))) &
            value_row.index.str.endswith("list_value")
            ]
        card_market_value_columns = value_row.index[
            value_row.index.str.startswith(tuple(list(Edition.list_names()))) &
            value_row.index.str.endswith("market_value")
            ]
        card_list_value = value_row[card_list_value_columns].sum()
        card_market_value = value_row[card_market_value_columns].sum()

    land_columns = value_row.index[
        value_row.index.str.startswith("deeds_value") |
        value_row.index.str.startswith("plot_value") |
        value_row.index.str.startswith("tract_value") |
        value_row.index.str.startswith("region_value") |
        (value_row.index.str.startswith("totem") & value_row.index.str.endswith("_value"))
        ]
    land_value = value_row[land_columns].sum()

    dec_columns = value_row.index[
        value_row.index.str.startswith("dec_value")
    ]
    dec_value = value_row[dec_columns].sum()

    sps_columns = value_row.index[
        value_row.index.str.startswith("sps_value") |
        value_row.index.str.startswith("spsp_value")
        ]
    sps_value = value_row[sps_columns].sum()

    other_columns = value_row.index[
        value_row.index.str.endswith("_value") &
        ~value_row.index.str.startswith("total_") &
        ~value_row.index.str.startswith(tuple(card_list_value_columns)) &
        ~value_row.index.str.startswith(tuple(card_market_value_columns)) &
        ~value_row.index.str.startswith(tuple(dec_columns)) &
        ~value_row.index.str.startswith(tuple(sps_columns)) &
        ~value_row.index.str.startswith(tuple(land_columns))
        ]
    other_value = value_row[other_columns].sum()

    cards = [
        create_value_card("Total",
                          ["Invested: ", str(round(invested_value, 2)) + " $",
                           html.Br(),
                           "Value: ", str(round(total_value, 2)) + " $"],
                          static_values_enum.coins_icon_url),
        create_value_card("Cards", [
            "List: " + str(round(card_list_value, 2)) + " $",
            html.Br(),
            "Market: " + str(round(card_market_value, 2)) + " $",
            ], static_values_enum.cards_icon_url),
        create_value_card("DEC", str(round(dec_value, 2)) + " $", static_values_enum.dec_icon_url),
        create_value_card("SPS", str(round(sps_value, 2)) + " $", static_values_enum.sps_icon_url),
        create_value_card("Land", str(round(land_value, 2)) + " $", static_values_enum.land_icon_url),
        create_value_card("Others", str(round(other_value, 2)) + " $", static_values_enum.other_icon_url)
    ]

    return [dbc.Row(html.H4("Values from: " + str(target_date))),
            dbc.Row([dbc.Col(card, width=1, lg=2) for card in cards])]
