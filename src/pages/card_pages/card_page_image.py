import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, State

from main import app
from src.pages.card_pages import card_page_ids

layout = dbc.Row(id=card_page_ids.card_image, style={'height': '100%'})


@app.callback(
    Output(card_page_ids.card_image, 'children'),
    Input(card_page_ids.filtered_cards_top_df, 'data'),
    State(card_page_ids.filter_cards_settings, 'data')
)
def update_top_cards(filtered_df, filter_settings):
    if not filtered_df:
        return "No card selected"

    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        # remove the card that is being searched for
        selected_card = filter_settings['selected-card']
        filtered_df = filtered_df.loc[filtered_df.card_name == selected_card]
        row = filtered_df.iloc[0]
        return dbc.Card(
            dbc.CardBody(
                dbc.CardImg(src=row.url, top=True, style={'height': '300px', 'objectFit': 'contain'}),
            )
        )
