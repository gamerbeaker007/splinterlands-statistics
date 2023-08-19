import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate
from main import app
from src.pages.card_pages import card_page_ids

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

    cards = []
    if not filtered_df.empty:
        # remove the card that is being searched for
        filtered_df = filtered_df.loc[filtered_df.card_name != filter_settings['selected-card']]
        filtered_df = filtered_df.head(5)
        for index, row in filtered_df.iterrows():
            cards.append(
                dbc.Card(
                    [
                        dbc.CardImg(src=row.url, top=True, style={'height': '200px', 'object-fit': 'contain'}),
                        dbc.CardBody([
                            html.P(str(row.card_name) + '\t\t★ combined', className='card-text'),
                            html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
                                   className='card-text'),
                            html.P('Battle count: ' + str(int(row.battles)), className='card-text'),
                            html.P('Win: ' + str(row.win_percentage) + '%', className='card-text'),
                        ]
                        ),
                    ],
                    style={'height': '450px'},
                    className='mb-3',
                )
            )

    return [dbc.Col(card) for card in cards]
