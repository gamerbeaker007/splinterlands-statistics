import dash_bootstrap_components as dbc
from dash import html


def get_card_columns(df, number, detailed=True, account=None):
    df = df.head(number)
    cards = []
    for index, row in df.iterrows():
        body = [html.H6(str(row.card_name) + '\t\t★ ' + str(row.level),
                        className='card-text',
                        style={'textAlign': 'center', 'marginBottom': '10px'}
                        )]

        if detailed:
            body.append(html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
                               className='card-text',
                               style={'textAlign': 'center', 'marginBottom': '5px'}
                               ))

        body.append(html.P('Battle count: ' + str(int(row.battles)),
                           className='card-text',
                           style={'textAlign': 'center', 'marginBottom': '5px'}
                           ))
        if detailed:
            body.append(html.P('Win: ' + str(row.win_percentage) + '%',
                               className='card-text',
                               style={'textAlign': 'center', 'marginBottom': '5px'}
                               ))

        if account:
            cards.append(
                dbc.CardLink(
                    dbc.Card(children=[
                            dbc.CardImg(src=row.url, top=True, style={'height': '200px', 'objectFit': 'contain'}),
                            dbc.CardBody(body),
                        ],
                        className='mb-3 card-hover',
                        style={'padding': '10px'},
                    ),
                    href='card?card_id=' + str(row.card_detail_id) + '#account=' + account,
                    style={'textDecoration': 'none',
                           'color': 'inherit'},
                ),
            )
        else:
            cards.append(
                dbc.Card(
                    [
                        dbc.CardImg(src=row.url, top=True, style={'height': '200px', 'objectFit': 'contain'}),
                        dbc.CardBody(body),
                    ],
                    className='mb-3',
                    style={'padding': '10px'}
                )
            )

    return [dbc.Col(card, className='mb-3') for card in cards]
