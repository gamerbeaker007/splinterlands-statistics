from datetime import datetime
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dcc, State
from dash.exceptions import PreventUpdate

from src.configuration import store
from src.graphs import portfolio_graph
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.portfolio_pages import portfolio_deposit, portfolio_editions, portfolio_sps, portfolio_ids
from src.static import static_values_enum
from src.static.static_values_enum import Edition
from src.utils import chart_util, store_util
from src.utils.trace_logging import measure_duration

layout = dbc.Container([
    dcc.Store(id=portfolio_ids.filtered_portfolio_df),
    dcc.Store(id=portfolio_ids.trigger_portfolio_update),

    dbc.Row([
        html.H1('Portfolio'),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Combine accounts'),
                    dcc.Dropdown(multi=True,
                                 id=portfolio_ids.dropdown_user_selection_portfolio,
                                 className='dbc',
                                 style={'min-width': '350px'},
                                 ),
                ],
                className='mb-3',
            ),
        ),
        dbc.Col(portfolio_deposit.get_deposit_layout(), className='mb-3'),
    ]),
    dbc.Row(id=portfolio_ids.update_values_row, className='mb-3'),
    dbc.Row(dcc.Graph(id=portfolio_ids.total_all_portfolio_graph), className='mb-3'),

    dbc.Row([
        dbc.Col(portfolio_editions.get_edition_layout(), className='mb-3'),
        dbc.Col(portfolio_sps.get_sps_layout(), className='mb-3'),

    ]),

    dbc.Row(dcc.Graph(id=portfolio_ids.all_portfolio_graph), className='mb-3'),
])


@app.callback(
    Output(portfolio_ids.dropdown_user_selection_portfolio, 'value'),
    Output(portfolio_ids.dropdown_user_selection_portfolio, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(
    Output(portfolio_ids.filtered_portfolio_df, 'data'),
    Input(portfolio_ids.dropdown_user_selection_portfolio, 'value'),
    Input(portfolio_ids.trigger_portfolio_update, 'data'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_filter_data(combine_users, trigger_portfolio, trigger_daily):
    if len(combine_users) == 0:
        raise PreventUpdate

    filtered_users = []
    for user in combine_users:
        if not store.portfolio.empty and not store.portfolio.loc[(store.portfolio.account_name == user)].empty:
            filtered_users.append(user)

    # only save when changed
    if store.view_portfolio_accounts.empty or store.view_portfolio_accounts.account_name.tolist() != combine_users:
        store.view_portfolio_accounts = pd.DataFrame({'account_name': filtered_users})
        store_util.save_single_store('view_portfolio_accounts')

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


@app.callback(
    Output(portfolio_ids.total_all_portfolio_graph, 'figure'),
    Input(portfolio_ids.filtered_portfolio_df, 'data'),
    State(portfolio_ids.dropdown_user_selection_portfolio, 'value'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_portfolio_total_graph(filtered_df, combined_users, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return portfolio_graph.plot_portfolio_total(temp_df, combined_users, theme)


@app.callback(
    Output(portfolio_ids.all_portfolio_graph, 'figure'),
    Input(portfolio_ids.filtered_portfolio_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_portfolio_all_graph(filtered_df, theme):
    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(StringIO(filtered_df), orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return portfolio_graph.plot_portfolio_all(temp_df, theme)


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
    Output(portfolio_ids.update_values_row, 'children'),
    Input(portfolio_ids.filtered_portfolio_df, 'data'),
    Input(portfolio_ids.total_all_portfolio_graph, 'clickData'),
)
@measure_duration
def display_click_data(filtered_portfolio_df, click_data):
    if not filtered_portfolio_df:
        raise PreventUpdate
    else:
        filtered_portfolio_df = pd.read_json(StringIO(filtered_portfolio_df), orient='split')

    if click_data:
        target_date = click_data['points'][0]['x']
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')

    if not filtered_portfolio_df.empty:
        filtered_portfolio_df.sort_values(by='date', inplace=True)
        filtered_portfolio_df = filtered_portfolio_df[filtered_portfolio_df['date'] <= target_date]

        # Determine invested amount
        invested_value = 0
        if 'total_investment_value' in filtered_portfolio_df.columns.tolist():
            investment_df = filtered_portfolio_df.loc[(filtered_portfolio_df.total_investment_value.notna())]
            if not investment_df.empty:
                invested_value = investment_df.iloc[-1].total_investment_value

        value_df = filtered_portfolio_df.loc[(filtered_portfolio_df.total_value.notna())]
        value_row = value_df.iloc[-1]

        total_value = value_row.total_value

        # For old version there might be a collection_list_value
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

        dec_staked_columns = value_row.index[
            value_row.index.str.startswith("dec_staked_value")
        ]
        dec_staked_value = value_row[dec_staked_columns].sum()

        sps_columns = value_row.index[
            value_row.index.str.startswith("sps_value")
        ]
        sps_value = value_row[sps_columns].sum()

        sps_staked_columns = value_row.index[
            value_row.index.str.startswith("spsp_value")
        ]
        sps_staked_value = value_row[sps_staked_columns].sum()

        other_columns = value_row.index[
            value_row.index.str.endswith("_value") &
            ~value_row.index.str.startswith("total_") &
            ~value_row.index.str.startswith(tuple(card_list_value_columns)) &
            ~value_row.index.str.startswith(tuple(card_market_value_columns)) &
            ~value_row.index.str.startswith(tuple(dec_columns)) &
            ~value_row.index.str.startswith(tuple(dec_staked_columns)) &
            ~value_row.index.str.startswith(tuple(sps_columns)) &
            ~value_row.index.str.startswith(tuple(sps_staked_columns)) &
            ~value_row.index.str.startswith(tuple(land_columns))
            ]
        other_value = value_row[other_columns].sum()
    else:
        invested_value = 0
        total_value = 0
        card_list_value = 0
        card_market_value = 0
        dec_value = 0
        dec_staked_value = 0
        sps_value = 0
        sps_staked_value = 0
        land_value = 0
        other_value = 0

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
        create_value_card("DEC",
                          [
                              "Liquid: " + str(round(dec_value, 2)) + " $",
                              html.Br(),
                              "Staked: " + str(round(dec_staked_value, 2)) + " $",
                          ],
                          static_values_enum.dec_icon_url),
        create_value_card("SPS",
                          [
                              "Liquid: " + str(round(sps_value, 2)) + " $",
                              html.Br(),
                              "Staked: " + str(round(sps_staked_value, 2)) + " $",
                          ],
                          static_values_enum.sps_icon_url),
        create_value_card("Land", str(round(land_value, 2)) + " $", static_values_enum.land_icon_url),
        create_value_card("Others", str(round(other_value, 2)) + " $", static_values_enum.other_icon_url)
    ]

    return [dbc.Row(html.H4("Values from: " + str(target_date))),
            dbc.Row([dbc.Col(card, width=1, lg=2) for card in cards])]
