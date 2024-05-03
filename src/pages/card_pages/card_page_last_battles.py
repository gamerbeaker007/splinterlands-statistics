from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input

from src.pages.card_pages import card_page_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.shared_modules import battles
from src.utils.trace_logging import measure_duration

layout = dbc.Row(
    dbc.Accordion(
        children=[
            dbc.AccordionItem(
                id=card_page_ids.battles_won,
                title='Last 5 won battles',
                className='dbc',
            ),
            dbc.AccordionItem(
                id=card_page_ids.battles_loss,
                title='Last 5 lost battles',
                className='dbc',
            )
        ],
        start_collapsed=True,
        className='mb-3'
    )
),


@app.callback(
    Output(card_page_ids.battles_won, 'children'),
    Output(card_page_ids.battles_loss, 'children'),
    Input(card_page_ids.filtered_cards_battle_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_last_battles(filtered_df, theme):
    if not filtered_df:
        return "No card selected"

    df = pd.read_json(StringIO(filtered_df), orient='split')
    account = df.account.tolist()[0]
    df.sort_values('created_date', inplace=True)
    last_win = df[df.result == 'win'].tail(5).battle_id.tolist()
    last_loss = df[df.result == 'loss'].tail(5).battle_id.tolist()
    result_layout_win = battles.get_battle_rows(account, last_win)
    result_layout_loss = battles.get_battle_rows(account, last_loss)

    return result_layout_win, result_layout_loss
