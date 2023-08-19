import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input
from dash.exceptions import PreventUpdate
from main import app


layout = dbc.Row(id='top-paired-cards')


@app.callback(
    Output('top-paired-cards', 'children'),
    Input('filtered-cards-df', 'data'),
)
def update_top_cards(filtered_df):
    if not filtered_df :
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
