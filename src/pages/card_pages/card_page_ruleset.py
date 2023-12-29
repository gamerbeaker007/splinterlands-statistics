from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input
from dash import html

from main import app
from src.pages.card_pages import card_page_ids
from src.utils.trace_logging import measure_duration

layout = dbc.Row(id=card_page_ids.card_ruleset,
                 style={'position': 'absolute',
                        'top': '50%',
                        'left': '50%',
                        'transform': 'translate(-50%,-50%)'})


@app.callback(
    Output(card_page_ids.card_ruleset, 'children'),
    Input(card_page_ids.filtered_cards_battle_df, 'data'),
)
@measure_duration
def update_top_cards(filtered_df):
    if not filtered_df:
        return "No card selected"

    result_layout = []

    filtered_df = pd.read_json(StringIO(filtered_df), orient='split')
    if not filtered_df.empty:
        ruleset_played = pd.concat([filtered_df.ruleset1, filtered_df.ruleset2, filtered_df.ruleset3]).value_counts()
        top_5 = ruleset_played.head(5)
        if not top_5.empty:
            result_layout.append(html.H6("Most played with ruleset top 5"))
            for index, value in top_5.items():
                result_layout.append(html.P(str(index) + ": " + str(value), style={'marginBottom': '5px'}))

        match_type = filtered_df.match_type.value_counts()
        if not match_type.empty:
            result_layout.append(html.H6("Match type used", style={'marginTop': '20px'}))
            for index, value in match_type.items():
                result_layout.append(html.P(str(index) + ": " + str(value), style={'marginBottom': '5px'}))

    return html.Div(result_layout)
