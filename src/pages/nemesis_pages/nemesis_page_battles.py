from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input
from dash.exceptions import PreventUpdate

from src.pages.main_dash import app
from src.pages.nemesis_pages import nemesis_page_ids
from src.pages.shared_modules import battles
from src.utils.trace_logging import measure_duration

layout = dbc.Row(id=nemesis_page_ids.opponent_battles)


@app.callback(
    Output(nemesis_page_ids.opponent_battles, 'children'),
    Input(nemesis_page_ids.filtered_against_df, 'data'),
)
@measure_duration
def update_battles(filtered_df):
    if not filtered_df:
        raise PreventUpdate

    result_layout = []
    filtered_df = pd.read_json(StringIO(filtered_df), orient='split')
    if not filtered_df.empty:
        last_battles = filtered_df.sort_values(by='created_date').tail(5).battle_id.tolist()
        account = filtered_df.account.tolist()[0]
        result_layout = battles.get_battle_rows(account, last_battles)

    return result_layout
