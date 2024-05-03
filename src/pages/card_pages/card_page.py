import dash_bootstrap_components as dbc
from dash import html, dcc

from src.pages.card_pages import weakest_cards, top_cards, card_page_filter, card_page_ids, card_page_info, \
    card_page_image, card_page_ruleset, card_page_last_battles

layout = dbc.Container([
    dbc.Row([
        html.H1('Specific card overview'),
        html.P('Select and account and card to view'),
    ]),
    dbc.Row(card_page_filter.layout),

    dbc.Row([
        dbc.Col(card_page_info.layout),
        dbc.Col(card_page_image.layout),
        dbc.Col(card_page_ruleset.layout, style={'position': 'relative'}),
    ], className='m-3'),

    dbc.Row(card_page_last_battles.layout),

    dbc.Row(top_cards.layout),
    dbc.Row(weakest_cards.layout),

    dcc.Store(id=card_page_ids.filtered_cards_top_df),
    dcc.Store(id=card_page_ids.filtered_cards_losing_df),
    dcc.Store(id=card_page_ids.filter_cards_settings),
    dcc.Store(id=card_page_ids.filtered_cards_battle_df),

    dcc.Store(id=card_page_ids.input_account_name),
    dcc.Store(id=card_page_ids.input_card_name),
])
