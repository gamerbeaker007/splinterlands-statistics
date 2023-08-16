import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc
from dash.exceptions import PreventUpdate

from main import app
from src import analyse
from src.configuration import store
from src.utils import store_util


filter_settings = {'selected-card': '',
                   'account': ''}

layout = dbc.Container([
    dbc.Row([
        html.H1('Specific card overview'),
        html.P('Select and account and card to view'),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(store_util.get_account_names(),
                                 value=store_util.get_first_account_name(),
                                 id='dropdown-user-selection-card-overview',
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Played cards'),
                    dcc.Dropdown(id='dropdown-card-selection',
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),

    ]),

    dbc.Row(id='top-paired-cards'),
    dbc.Row(id='weakest-against-cards'),
    dbc.Row([
        dbc.Accordion(
            dbc.AccordionItem(html.Div(id='card-overview-table', className='dbc'),
                              title='Complete table',
                              ),
            start_collapsed=True,
        )
    ]),
    dcc.Store(id='filtered-cards-df'),
    dcc.Store(id='filtered-cards-losing-df'),
    dcc.Store(id='filter-cards-settings'),

])


@app.callback(
    Output('card-overview-table', 'children'),
    Input('filtered-cards-df', 'data'),
)
def update_main_table(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        return dash_table.DataTable(
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns=[
                {'id': 'url_markdown', 'name': 'Card', 'presentation': 'markdown'},
                {'id': 'card_name', 'name': 'Name'},
                {'id': 'level', 'name': 'Level'},
                # {'id': 'win_to_loss_ratio', 'name': 'win_to_loss_ratio'},
                {'id': 'battles', 'name': 'Battles'},
                # {'id': 'win_ratio', 'name': 'win_ratio'},
                {'id': 'win_percentage', 'name': 'Win Percentage'},
            ],
            data=filtered_df.to_dict('records'),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action='native',
            sort_action='native',
            style_table={'overflowX': 'auto'},
            style_cell_conditional=[{'if': {'column_id': 'url'}, 'width': '200px'}, ],
            page_size=10,
        ),
    else:
        return dash_table.DataTable()


@app.callback(
    Output('top-paired-cards', 'children'),
    Input('filtered-cards-df', 'data'),
)
def update_top_cards(filtered_df):
    if not filtered_df :
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    cards = []
    if not filtered_df.empty:
        filtered_df = filtered_df.head(5)
        for index, row in filtered_df.iterrows():
            cards.append(
                dbc.Card(
                    [
                        dbc.CardImg(src=row.url, top=True, style={'height': '200px', 'object-fit': 'contain'}),
                        dbc.CardBody([
                            html.P(str(row.card_name) + '\t\t★' + str(row.level), className='card-text'),
                            html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
                                   className='card-text'),
                            html.P('Battle count: ' + str(int(row.battles)), className='card-text'),
                            html.P('Win: ' + str(row.win_percentage) + '%', className='card-text'),
                        ]
                        ),
                    ],
                    style={'height': '375px'},
                    className='mb-3',
                )
            )

    return [dbc.Col(card) for card in cards]


@app.callback(
    Output('weakest-against-cards', 'children'),
    Input('filtered-cards-losing-df', 'data'),
)
def update_weakest_cards(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    cards = []
    if not filtered_df.empty:
        filtered_df = filtered_df.head(5)
        for index, row in filtered_df.iterrows():
            cards.append(
                dbc.Card(
                    [
                        dbc.CardImg(src=row.url, top=True, style={'height': '200px', 'object-fit': 'contain'}),
                        dbc.CardBody([
                            html.P(str(row.card_name) + '\t\t★' + str(row.level), className='card-text'),
                            html.P('Battle count: ' + str(int(row.battles)), className='card-text'),
                        ]
                        ),
                    ],
                    style={'height': '375px'},
                    className='mb-3',
                )
            )

    return [dbc.Col(card) for card in cards]


@app.callback(Output('filtered-cards-df', 'data'),
              Output('filtered-cards-losing-df', 'data'),
              Input('filter-cards-settings', 'data'))
def filter_cards_df(store_filter_settings):
    if store_filter_settings is None or store_filter_settings['account'] == '':
        raise PreventUpdate

    # Filter before processing is done
    my_team = analyse.filter_battles(store.battle_big, filter_account=store_filter_settings['account'])
    my_team = analyse.get_battles_with_used_card(my_team, store_filter_settings['selected-card'])
    battle_ids = my_team.battle_id.tolist()

    # Processing
    my_team = analyse.process_battles_win_percentage(my_team)

    losing_against = analyse.filter_battles(store.losing_big, filter_account=store_filter_settings['account'])
    losing_against = analyse.get_losing_battles(losing_against, battle_ids)

    # Processing
    losing_against['result'] = 'loss'
    losing_against = analyse.process_battles_win_percentage(losing_against)

    # TODO sort by?

    return (my_team.to_json(date_format='iso', orient='split'),
            losing_against.to_json(date_format='iso', orient='split'))


@app.callback(Output('filter-cards-settings', 'data'),
              Input('dropdown-user-selection-card-overview', 'value'),
              Input('dropdown-card-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def filter_battle_df(account,
                     selected_card,
                     trigger_daily):
    filter_settings['account'] = account
    filter_settings['selected-card'] = selected_card
    return filter_settings


@app.callback(Output('dropdown-card-selection', 'value'),
              Output('dropdown-card-selection', 'options'),
              Input('dropdown-user-selection-card-overview', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def update_card_list(user_selection, tigger):
    df = analyse.filter_battles(store.battle_big, filter_account=user_selection)
    played_cards = df.card_name.unique().tolist()

    return played_cards[0], played_cards


