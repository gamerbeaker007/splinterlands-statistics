import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, State
from dash.exceptions import PreventUpdate

from main import app
from src import analyse
from src.pages.card_pages import card_page_ids

layout = dbc.Row(id=card_page_ids.card_info, style={'position': 'absolute',
                                                    'top': '50%',
                                                    'left': '50%',
                                                    'transform': 'translate(-50%,-50%)'})


@app.callback(
    Output(card_page_ids.card_info, 'children'),
    Input(card_page_ids.filtered_cards_top_df, 'data'),
    State(card_page_ids.filter_cards_settings, 'data')
)
def update_top_cards(filtered_df, filter_settings):
    if not filtered_df:
        raise PreventUpdate

    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        # remove the card that is being searched for
        filtered_df = filtered_df.loc[filtered_df.card_name == filter_settings['selected-card']]
        row = filtered_df.iloc[0]
        max_level_owned = analyse.get_max_card_of_collection(filter_settings['account'],
                                                             filter_settings['selected-card'])
        return html.Div(
            [
                html.H5('Battle statistics'),
                html.P(str(row.card_name) + '\t\t★ ' + str(max_level_owned),
                       style={'margin-bottom': '5px'}),
                html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
                       style={'margin-bottom': '5px'}),
                html.P('Battle count: ' + str(int(row.battles)),
                       style={'margin-bottom': '5px'}),
                html.P('Win: ' + str(row.win_percentage) + '%',
                       style={'margin-bottom': '5px'}),
            ],
            className='mb-3',
        )
