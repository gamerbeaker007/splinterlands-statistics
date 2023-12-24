import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State

from main import app
from src.pages.card_pages import card_page_ids, card_page_mana_graph

layout = dbc.Row([
        html.Div(id=card_page_ids.card_info),
        html.Div(card_page_mana_graph.layout),
    ])


@app.callback(
    Output(card_page_ids.card_info, 'children'),
    Input(card_page_ids.filtered_cards_top_df, 'data'),
    State(card_page_ids.filter_cards_settings, 'data')
)
def update_top_cards(filtered_df, filter_settings):
    if not filtered_df:
        return "No card selected"

    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        # remove the card that is being searched for
        filtered_df = filtered_df.loc[filtered_df.card_name == filter_settings['selected-card']]
        row = filtered_df.iloc[0]

        return html.Div(
            [
                html.H5('Battle statistics'),
                html.P(str(row.card_name) + '\t\t★ ' + str(row.level),
                       style={'marginBottom': '5px'}),
                html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
                       style={'marginBottom': '5px'}),
                html.P('Battle count: ' + str(int(row.battles)),
                       style={'marginBottom': '5px'}),
                html.P('Win: ' + str(row.win_percentage) + '%',
                       style={'marginBottom': '5px'}),
            ],
        )
