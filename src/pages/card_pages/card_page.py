import dash_bootstrap_components as dbc
from dash import html, dcc

from src.pages.card_pages import weakest_cards, top_cards, card_page_filter

layout = dbc.Container([
    dbc.Row([
        html.H1('Specific card overview'),
        html.P('Select and account and card to view'),
    ]),
    dbc.Row(card_page_filter.layout),

    dbc.Row([
        dbc.Col(html.H1('Col1 (detailed)')),
        dbc.Col(html.H1('Col2 (image)')),
        dbc.Col(html.H1('Col3 (ruleset)')),
    ]),

    dbc.Row(top_cards.layout),
    dbc.Row(weakest_cards.layout),


    dcc.Store(id='filtered-cards-df'),
    dcc.Store(id='filtered-cards-losing-df'),
    dcc.Store(id='filter-cards-settings'),

    dcc.Store(id='input_account_name'),
    dcc.Store(id='input_card_name'),

])

