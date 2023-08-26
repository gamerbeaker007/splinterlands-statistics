import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate
from main import app
from src import analyse
from src.pages.card_pages import card_page_ids

layout = dbc.Row(id=card_page_ids.card_image)


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
        max_level_owned = analyse.get_max_card_of_collection(filter_settings['account'], selected_card)
        image_url = analyse.get_image_url(selected_card, max_level_owned, row.edition)
        return dbc.Card(
            [
                dbc.CardBody([
                    dbc.CardImg(src=image_url, top=True, style={'height': '300px', 'object-fit': 'contain'}),
                ]
                ),
            ],
            style={'height': '350px'},
            className='mb-3',
        )