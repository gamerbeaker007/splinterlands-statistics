import datetime

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc, ctx, State
from dash.exceptions import PreventUpdate
from dateutil import parser

from main import app
from src import analyse
from src.configuration import store
from src.pages import filter_page
from src.static.static_values_enum import Element, Edition, CardType, Rarity, ManaCap
from src.utils import store_util

btn_active_color = '#222'
btn_inactive_color = '#bdbfbe'

filter_settings = {}
for element in Element:
    filter_settings[element.name] = False
for edition in Edition:
    filter_settings[edition.name] = False
for card_type in CardType:
    filter_settings[card_type.name] = False
for rarity in Rarity:
    filter_settings[rarity.name] = False
for mana_cap in ManaCap:
    filter_settings[mana_cap.name] = False

filter_settings['minimal-battles'] = 0
filter_settings['from_date'] = datetime.datetime(2000, 1, 1)
filter_settings['rule_sets'] = []
filter_settings['account'] = ''
filter_settings['sort_by'] = []

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics battles'),
        html.P('Your battle statistics of your summoners and monster'),
        dbc.Col(html.H4('Filter')),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(store_util.get_account_names(),
                                 value=store_util.get_first_account_name(),
                                 id='dropdown-user-selection',
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),
    ]),
    dbc.Row([
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(CardType))),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(Rarity))),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(Element))),
        dbc.Col(dbc.ButtonGroup(filter_page.get_filter_buttons(Edition))),
    ], className='mb-3'),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Minimal battles'),
                    dbc.Input(id='minimal-battles-filter',
                              min=0,
                              value=0,
                              type='number',
                              pattern='[0-9]')
                ],
                className='mb-3',
            )
        ),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Mana cap'),
                    dbc.ButtonGroup(filter_page.get_filter_buttons_text(ManaCap)),
                ],
                className='mb-3',
            )
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Since season'),
                    dcc.Dropdown(id='dropdown-season-selection',
                                 clearable=False,
                                 style={'width': '85px'},
                                 className='dbc'),
                    dbc.InputGroupText(id='filter-from-date')

                ],
                className='mb-3',
            ),
        ),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Rule sets'),
                    dcc.Dropdown(options=store_util.get_rule_sets_list(),
                                 id='dropdown-rule-sets-selection',
                                 multi=True,
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
        ),
    ]),

    dbc.Row([
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Sort by'),
                    dcc.Dropdown(options=['battles', 'percentage', 'win', 'loss'],
                                 value=['battles'],
                                 id='dropdown-sort-by-selection',
                                 multi=True,
                                 className='dbc',
                                 style={'width': '50%'},
                                 ),

                ],
                className='mb-3',
            ),
        ),
    ]),

    dbc.Row(id='top-cards'),
    dbc.Row([
        dbc.Accordion(
            dbc.AccordionItem(html.Div(id='main-table', className='dbc'),
                              title='Complete table',
                              ),
            start_collapsed=True,
        )
    ]),
    dcc.Store(id='filtered-battle-df'),
    dcc.Store(id='filter-settings'),
])


@app.callback(Output('dropdown-season-selection', 'options'),
              Output('dropdown-season-selection', 'value'),
              Input('trigger-daily-update', 'data'))
def update_seasons_played_list(tigger):
    season_played = store_util.get_seasons_played_list()
    first_played_season = ''
    if len(season_played) > 0:
        first_played_season = season_played[-1]
    return season_played, first_played_season

@app.callback(
    Output('main-table', 'children'),
    Input('filtered-battle-df', 'data'),
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
    Output('top-cards', 'children'),
    Input('filtered-battle-df', 'data'),
)
def update_top_cards(filtered_df):
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


@app.callback(Output('filtered-battle-df', 'data'),
              Input('filter-settings', 'data'))
def filter_battle_df(store_filter_settings):
    if store_filter_settings is None or store_filter_settings['account'] == '':
        raise PreventUpdate

    # Filter before processing is done
    df = analyse.filter_battles(store.battle_big, filter_account=store_filter_settings['account'])
    df = analyse.filter_date(df, filter_settings)
    df = analyse.filter_mana_cap(df, filter_settings)
    df = analyse.filter_rule_sets(df, filter_settings)

    # Processing
    df = analyse.process_battles_win_percentage(df)

    # Filter after processing is done
    df = analyse.filter_element(df, filter_settings)
    df = analyse.filter_edition(df, filter_settings)
    df = analyse.filter_card_type(df, filter_settings)
    df = analyse.filter_rarity(df, filter_settings)
    df = analyse.filter_battle_count(df, filter_settings['minimal-battles'])
    df = analyse.sort_by(df, filter_settings['sort_by'])

    return df.to_json(date_format='iso', orient='split')


@app.callback(Output('filter-settings', 'data'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def filter_battle_df(account,
                     trigger_daily):
    filter_settings['account'] = account
    return filter_settings


@app.callback(Output('filter-settings', 'data'),
              Output('filter-from-date', 'children'),
              Input('dropdown-season-selection', 'value'))
def filter_season_df(season_id):
    if season_id:
        season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
        from_date = parser.parse(season_end_date)

        filter_settings['from_date'] = from_date
        return filter_settings, str(from_date.strftime("%Y-%m-%d %H:%M (UTC)"))
    else:
        return filter_settings, ""


@app.callback(Output('filter-settings', 'data'),
              Input('dropdown-sort-by-selection', 'value'))
def sort_by(sorts):
    filter_settings['sort_by'] = sorts
    return filter_settings


@app.callback(Output('filter-settings', 'data'),
              Input('dropdown-rule-sets-selection', 'value'))
def filter_season_df(rule_sets):
    filter_settings['rule_sets'] = rule_sets
    return filter_settings


@app.callback(Output('filter-settings', 'data'),
              Input('minimal-battles-filter', 'value'),
              )
def update_minimal_battle_filter(value):
    if not value:
        value = 0

    filter_settings['minimal-battles'] = value
    return filter_settings


def update_style(n_clicks, style):
    bg_color = btn_active_color if is_active(n_clicks) else btn_inactive_color
    style['background-color'] = bg_color
    return style


for element in Element:
    @app.callback(Output('{}-filter-button'.format(element.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(element.name), 'n_clicks'),
                  State('{}-filter-button'.format(element.name), 'style')
                  )
    def on_click(n_clicks, style):
        style = update_style(n_clicks, style)
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        filter_settings[setting] = is_active(n_clicks)
        return style, filter_settings

for edition in Edition:
    @app.callback(Output('{}-filter-button'.format(edition.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(edition.name), 'n_clicks'),
                  State('{}-filter-button'.format(edition.name), 'style')
                  )
    def on_click(n_clicks, style):
        style = update_style(n_clicks, style)
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        filter_settings[setting] = is_active(n_clicks)
        return style, filter_settings

for card_type in CardType:
    @app.callback(Output('{}-filter-button'.format(card_type.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(card_type.name), 'n_clicks'),
                  State('{}-filter-button'.format(card_type.name), 'style')
                  )
    def on_click(n_clicks, style):
        style = update_style(n_clicks, style)
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        filter_settings[setting] = is_active(n_clicks)
        return style, filter_settings

for rarity in Rarity:
    @app.callback(Output('{}-filter-button'.format(rarity.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(rarity.name), 'n_clicks'),
                  State('{}-filter-button'.format(rarity.name), 'style')
                  )
    def on_click(n_clicks, style):
        style = update_style(n_clicks, style)
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        filter_settings[setting] = is_active(n_clicks)
        return style, filter_settings

for mana_cap in ManaCap:
    @app.callback(Output('{}-filter-button'.format(mana_cap.name), 'style'),
                  Output('filter-settings', 'data'),
                  Input('{}-filter-button'.format(mana_cap.name), 'n_clicks'),
                  State('{}-filter-button'.format(mana_cap.name), 'style')
                  )
    def on_click(n_clicks, style):
        style = update_style(n_clicks, style)
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        filter_settings[setting] = is_active(n_clicks)
        return style, filter_settings


def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False
