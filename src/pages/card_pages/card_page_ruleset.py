import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input
from dash import html
from dash.exceptions import PreventUpdate

from main import app
from src.pages.card_pages import card_page_ids

layout = dbc.Row(id=card_page_ids.card_ruleset, style={'position': 'absolute',
                                                       'top': '50%',
                                                       'left': '50%',
                                                       'transform': 'translate(-50%,-50%)'})


@app.callback(
    Output(card_page_ids.card_ruleset, 'children'),
    Input(card_page_ids.filtered_cards_battle_df, 'data'),
)
def update_top_cards(filtered_df):
    if not filtered_df:
        raise PreventUpdate
    result_layout = []

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        ruleset_played = pd.concat([filtered_df.ruleset1, filtered_df.ruleset2, filtered_df.ruleset3]).value_counts()
        top_5 = ruleset_played.head(5)
        if not top_5.empty:
            result_layout.append(html.H6("Most payed with ruleset (5)"))
            for index, value in top_5.items():
                result_layout.append(html.P(str(index) + "(" + str(value) + ")", style={'margin-bottom': '5px'}))

        match_type = filtered_df.match_type.value_counts()
        if not match_type.empty:
            result_layout.append(html.H6("Match type used", style={'margin-top': '20px'}))
            for index, value in match_type.items():
                result_layout.append(html.P(str(index) + "(" + str(value) + ")", style={'margin-bottom': '5px'}))


    return html.Div(result_layout)

        # # remove the card that is being searched for
        # filtered_df = filtered_df.loc[filtered_df.card_name == filter_settings['selected-card']]
        # row = filtered_df.iloc[0]
        # max_level_owned = analyse.get_max_card_of_collection(filter_settings['account'],
        #                                                      filter_settings['selected-card'])
        # return html.Div(
        #     [
        #         html.H4('Card statistics'),
        #         html.P(str(row.card_name) + '\t\t★ ' + str(max_level_owned)),
        #         html.P('Battles (W-L): ' + str(int(row.win)) + '-' + str(int(row.loss)),
        #                className='card-text'),
        #         html.P('Battle count: ' + str(int(row.battles))),
        #         html.P('Win: ' + str(row.win_percentage) + '%'),
        #     ],
        #     className='mb-3',
        # )
