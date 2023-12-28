from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input
from dash import html
from dash.exceptions import PreventUpdate

from main import app
from src.pages.nemesis_pages import nemesis_page_ids
from src.utils.trace_logging import measure_duration

layout = dbc.Row(id=nemesis_page_ids.opponent_stats, className='mb-3')


@app.callback(
    Output(nemesis_page_ids.opponent_stats, 'children'),
    Input(nemesis_page_ids.filtered_against_df, 'data'),
)
@measure_duration
def update_opponent(filtered_df):
    if not filtered_df:
        raise PreventUpdate
    result_layout = []

    filtered_df = pd.read_json(StringIO(filtered_df), orient='split')
    if not filtered_df.empty:
        match_type = filtered_df.match_type.value_counts()
        if not match_type.empty:
            result_layout.append(html.H5("Battles", style={'marginTop': '20px'}))
            for index, value in match_type.items():
                col_result = []
                win = filtered_df.loc[(filtered_df.match_type == index) &
                                      (filtered_df.result == 'win')].result.count()
                loss = filtered_df.loc[(filtered_df.match_type == index) &
                                       (filtered_df.result == 'loss')].result.count()
                col_result.append(html.H6(str(index) + ':', style={'marginTop': '10px', 'marginBottom': '0px'}))
                col_result.append(html.P('Encounters: ' + str(value), style={'marginBottom': '0px'}))
                col_result.append(html.P('Win/Loss: ' + str(win) + '-' + str(loss), style={'marginBottom': '0px'}))
                col_result.append(html.P('Win pct : ' + str(round(win / (win + loss) * 100, 2)) + '%',
                                         style={'marginBottom': '0px'}))
                result_layout.append(dbc.Col(children=col_result))

    return result_layout
