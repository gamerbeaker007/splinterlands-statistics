import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input
from dash.exceptions import PreventUpdate

from main import app
from src.pages.card_pages import card_page_ids

layout = dbc.Row([dbc.Row(html.H1("Weakest against")),
                  dbc.Row(id=card_page_ids.weakest_against_cards)])


@app.callback(
    Output(card_page_ids.weakest_against_cards, 'children'),
    Input(card_page_ids.filtered_cards_losing_df, 'data'),
)
def update_weakest_cards(filtered_df):
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
                            html.P(str(row.card_name) + '\t\t★ combined', className='card-text'),
                            html.P('Battle count: ' + str(int(row.battles)), className='card-text'),
                        ]
                        ),
                    ],
                    style={'height': '300px'},
                    className='mb-3',
                )
            )

    return [dbc.Col(card) for card in cards]
