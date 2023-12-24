import threading

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc, State
from dash.exceptions import PreventUpdate

from main import app, measure_duration
from src import analyse
from src.configuration import store
from src.pages.card_pages import card
from src.pages.filter_pages import filter_user, filter_card_type, filter_rarity, filter_element, \
    filter_editions, filter_ids, filter_sort_by, filter_group_levels, filter_battle_format, \
    filter_ruleset, filter_season, filter_mana_cap, filter_battle_count

# This line need to be here to be tread safe cannot be place in
filter_settings_lock = threading.Lock()

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics battles'),
        html.P('Your battle statistics of your summoners and monster'),
        dbc.Col(html.H4('Filter')),
    ]),
    dbc.Row([
        dbc.Col(filter_user.layout, md=4),
    ]),
    dbc.Row([
        dbc.Col(filter_card_type.layout),
        dbc.Col(filter_rarity.layout),
        dbc.Col(filter_element.layout),
        dbc.Col(filter_editions.layout),
    ], className='mb-3'),
    dbc.Row([
        dbc.Col(filter_battle_count.layout),
        dbc.Col(filter_mana_cap.layout)
    ]),
    dbc.Row([
        dbc.Col(filter_season.layout),
        dbc.Col(filter_ruleset.layout),
        dbc.Col(filter_battle_format.layout),
    ]),

    dbc.Row([
        dbc.Col(filter_sort_by.layout),
        dbc.Col(filter_group_levels.layout),
    ]),

    dbc.Row(id='top-cards'),
    dbc.Row([
        dbc.Accordion(
        dbc.AccordionItem(html.Div(id='main-table-div', className='dbc'),
                              title='Complete table',
                              id='complete-table-accordion-item'
                              ),
            start_collapsed=True,
            id='accordion',
        )
    ]),
    html.Div(id='redirect-div'),
    dcc.Store(id='filtered-battle-df'),
    dcc.Store(id=filter_ids.filter_settings, data={}),

])



@app.callback(
    Output('main-table-div', 'children'),
    Input('filtered-battle-df', 'data'),
)
@measure_duration
def update_main_table(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        return dash_table.DataTable(id='top-cards-table',
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
        return dash_table.DataTable(id='top-cards-table-empty')


@app.callback(
    Output('redirect-div', 'children'),
    Input('top-cards-table', 'active_cell'),
    State('top-cards-table', 'derived_virtual_data'),
    State(filter_ids.filter_settings, 'data')
)
@measure_duration
def redirect_to_page(active_cell, data, stored_filter_settings):
    if active_cell:
        return dcc.Location(
            href='card?card_id=' + str(data[active_cell['row']]['card_detail_id'])
                 + '#account=' + str(stored_filter_settings['account'])
            , id='url-redirect')


@app.callback(
    Output('top-cards', 'children'),
    Input('filtered-battle-df', 'data'),
    State(filter_ids.filter_settings, 'data')
)
@measure_duration
def update_top_cards(filtered_df, stored_filter_settings):
    if not filtered_df:
        raise PreventUpdate

    account_name = stored_filter_settings['account']

    filtered_df = pd.read_json(filtered_df, orient='split')

    result_layout = []
    if not filtered_df.empty:
        result_layout = card.get_card_columns(account_name, filtered_df, 5)

    return result_layout


@app.callback(Output('filtered-battle-df', 'data'),
              Input(filter_ids.filter_settings, 'data'))
@measure_duration
def filter_battle_df(filter_settings):
    with filter_settings_lock:
        print(str(len(filter_settings)) + "filter settings: " + str(filter_settings))
        if filter_settings is {} or 'account' not in filter_settings:
            raise PreventUpdate

        # Filter before processing is done
        df = analyse.filter_battles(store.battle_big, filter_account=filter_settings['account'])
        df = analyse.filter_date(df, filter_settings)
        df = analyse.filter_mana_cap(df, filter_settings)
        df = analyse.filter_rule_sets(df, filter_settings)
        df = analyse.filter_format(df, filter_settings)

        # Processing
        group_levels = False
        if 'group_levels' in filter_settings:
            group_levels = filter_settings['group_levels']

        df = analyse.process_battles_win_percentage(df,
                                                    group_levels=group_levels)

        # Filter after processing is done
        df = analyse.filter_element(df, filter_settings)
        df = analyse.filter_edition(df, filter_settings)
        df = analyse.filter_card_type(df, filter_settings)
        df = analyse.filter_rarity(df, filter_settings)
        df = analyse.filter_battle_count(df, filter_settings)
        df = analyse.sort_by(df, filter_settings)

        return df.to_json(date_format='iso', orient='split')


