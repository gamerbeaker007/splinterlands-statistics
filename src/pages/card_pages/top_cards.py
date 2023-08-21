import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate
from main import app
from src.pages.card_pages import card_page_ids, card
from src.static.static_values_enum import CardType

layout = dbc.Row([dbc.Row(html.H1("Top paired cards")),
                  dbc.Row(id=card_page_ids.top_paired_cards)])


@app.callback(
    Output(card_page_ids.top_paired_cards, 'children'),
    Input(card_page_ids.filtered_cards_top_df, 'data'),
    State(card_page_ids.filter_cards_settings, 'data')
)
def update_top_cards(filtered_df, filter_settings):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    result_layout = []

    if not filtered_df.empty:
        # remove the card that is being searched for
        filtered_df = filtered_df.loc[filtered_df.card_name != filter_settings['selected-card']]

        summoners_df = filtered_df.loc[filtered_df.card_type == CardType.summoner.value]
        if not summoners_df.empty:
            result_layout.append(dbc.Row(html.H3("Most paired with summoner (2)")))
            result_layout.append(dbc.Row(card.get_card_columns(summoners_df, 2)))

        monsters_df = filtered_df.loc[filtered_df.card_type == CardType.monster.value]
        if not monsters_df.empty:
            result_layout.append(dbc.Row(html.H3("Most paired with units (5)")))
            result_layout.append(dbc.Row(card.get_card_columns(monsters_df, 5)))

        return result_layout
