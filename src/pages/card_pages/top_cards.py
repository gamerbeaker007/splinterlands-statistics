from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State

from src.pages.main_dash import app
from src.pages.card_pages import card_page_ids, card
from src.static.static_values_enum import CardType
from src.utils.trace_logging import measure_duration

layout = dbc.Row([dbc.Row(html.H1("Top paired cards")),
                  dbc.Row(id=card_page_ids.top_paired_cards)])


@app.callback(
    Output(card_page_ids.top_paired_cards, 'children'),
    Input(card_page_ids.filtered_cards_top_df, 'data'),
    State(card_page_ids.filter_cards_settings, 'data')
)
@measure_duration
def update_top_cards(filtered_df, stored_filter_settings):
    if not filtered_df:
        return "No card selected"

    filtered_df = pd.read_json(StringIO(filtered_df), orient='split')

    result_layout = []

    if not filtered_df.empty:
        account = stored_filter_settings['account']
        # remove the card that is being searched for
        filtered_df = filtered_df.loc[filtered_df.card_name != stored_filter_settings['selected-card']]

        summoners_df = filtered_df.loc[filtered_df.card_type == CardType.summoner.value]
        if not summoners_df.empty:
            result_layout.append(dbc.Row(html.H3("Most paired with summoner (2)")))
            result_layout.append(dbc.Row(card.get_card_columns(summoners_df, 2, account=account)))

        monsters_df = filtered_df.loc[filtered_df.card_type == CardType.monster.value]
        if not monsters_df.empty:
            result_layout.append(dbc.Row(html.H3("Most paired with units (5)")))
            result_layout.append(dbc.Row(card.get_card_columns(monsters_df, 5, account=account)))

        return result_layout
    else:
        return "No data found"
