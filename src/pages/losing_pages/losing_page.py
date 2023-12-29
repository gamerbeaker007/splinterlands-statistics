from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
from dash import html, Output, Input, dcc
from dash.exceptions import PreventUpdate
from dash_bootstrap_components import Container

from src import analyse
from src.configuration import store
from src.pages.card_pages import card
from src.pages.filter_pages import filter_season, filter_ruleset, \
    filter_battle_format, filter_mana_cap, filter_element, filter_rarity, filter_editions, filter_card_type, \
    filter_user, filter_ids, filter_battle_count, filter_group_levels
from src.pages.losing_pages import losing_ids
from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration

layout: Container = dbc.Container([
    dbc.Row([
        html.H1('Statistics losing battles'),
        html.P('Summoners and monster you lose most against'),
        dbc.Col(html.P('Filter on')),
        # dbc.Col(dcc.Dropdown(id='dropdown-user-selection-losing',
        #                      className='dbc'),
        #         ),
        # dbc.Col(dcc.Dropdown(options=['ALL'] + CardType.list_values(),
        #                      value='ALL',
        #                      id='dropdown-type-selection-losing',
        #                      className='dbc')),
        # dbc.Col(dcc.Dropdown(options=['ALL'] + MatchType.list_values(),
        #                      value='ALL',
        #                      id='dropdown-match-type-selection-losing',
        #                      className='dbc'))
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
        dbc.Col(filter_group_levels.layout),
    ]),

    dbc.Row(id=losing_ids.losing_cards),
    dbc.Row([
        dbc.Accordion(
            dbc.AccordionItem(
                id=losing_ids.complete_table,
                title='Complete table',
                className='dbc',
            ),
            start_collapsed=True,
            id=losing_ids.accordion,
        )
    ]),
    dcc.Store(id=filter_ids.filter_settings, data={}),

    dcc.Store(id=losing_ids.filtered_losing_df)

])


@app.callback(
    Output(losing_ids.filtered_losing_df, 'data'),
    Input(filter_ids.filter_settings, 'data'),
)
@measure_duration
def filter_battle_df(filter_settings):
    if (filter_settings is {}
            or 'account' not in filter_settings
            or filter_settings['account'] == ''):
        raise PreventUpdate

    # Filter before processing is done
    df = analyse.filter_battles(store.losing_big, filter_account=filter_settings['account'])
    df = analyse.filter_date(df, filter_settings)
    df = analyse.filter_mana_cap(df, filter_settings)
    df = analyse.filter_rule_sets(df, filter_settings)
    df = analyse.filter_format(df, filter_settings)

    # Filter after processing is done
    df = analyse.filter_element(df, filter_settings)
    df = analyse.filter_edition(df, filter_settings)
    df = analyse.filter_card_type(df, filter_settings)
    df = analyse.filter_rarity(df, filter_settings)
    # df = analyse.sort_by(df, filter_settings)

    group_levels = True
    if 'group_levels' in filter_settings:
        group_levels = filter_settings['group_levels']

    columns = ['card_detail_id', 'card_name', 'edition']
    if not group_levels:
        columns.append('level')

    df = df.groupby(columns, as_index=False).agg(battles=pd.NamedAgg(column='xp', aggfunc='count'),
                                                 level=pd.NamedAgg(column='level', aggfunc='max'))

    df = analyse.filter_battle_count(df, filter_settings)

    # count the losses with the filtered data
    df.sort_values('battles', ascending=False, inplace=True)

    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output(losing_ids.complete_table, 'children'),
    Input(losing_ids.filtered_losing_df, 'data'),
)
@measure_duration
def update_losing_table(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    df = pd.read_json(StringIO(filtered_df), orient='split')
    if not df.empty:
        df['url_markdown'] = df.apply(lambda row: analyse.get_image_url_markdown(row['card_name'],
                                                                                 row['level'],
                                                                                 row['edition']), axis=1)
        df['url'] = df.apply(lambda row: analyse.get_image_url(row['card_name'],
                                                               row['level'],
                                                               row['edition']), axis=1)

        df = df[['url_markdown', 'card_name', 'level', 'battles']]
        return dash_table.DataTable(
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns=[
                {'id': 'url_markdown', 'name': 'Card', 'presentation': 'markdown'},
                {'id': 'card_name', 'name': 'Name'},
                {'id': 'level', 'name': 'Level'},
                {'id': 'battles', 'name': 'battles'},

            ],
            data=df.to_dict('records'),
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
    Output(losing_ids.losing_cards, 'children'),
    Input(losing_ids.filtered_losing_df, 'data'),
)
@measure_duration
def update_top_cards(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(StringIO(filtered_df), orient='split')

    result_layout = []
    if not filtered_df.empty:
        filtered_df['url'] = filtered_df.apply(lambda row: analyse.get_image_url(row['card_name'],
                                                                                 row['level'],
                                                                                 row['edition']), axis=1)
        result_layout = card.get_card_columns(filtered_df, 5, detailed=False)

    return result_layout
