import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input
from dash import html
from dash.exceptions import PreventUpdate

from main import app
from src.pages.nemesis_pages import nemesis_page_ids

layout = dbc.Row(id=nemesis_page_ids.opponent_stats, className='mb-3')


@app.callback(
    Output(nemesis_page_ids.opponent_stats, 'children'),
    Input(nemesis_page_ids.filtered_against_df, 'data'),
)
def update_opponent(filtered_df):
    if not filtered_df:
        raise PreventUpdate
    result_layout = []

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        match_type = filtered_df.match_type.value_counts()
        col_result = []
        if not match_type.empty:
            col_result.append(html.H5("Battles", style={'margin-top': '20px'}))
            for index, value in match_type.items():
                win = filtered_df.loc[(filtered_df.match_type == index) &
                                      (filtered_df.result == 'win')].result.count()
                loss = filtered_df.loc[(filtered_df.match_type == index) &
                                       (filtered_df.result == 'loss')].result.count()
                col_result.append(html.H6(str(index) + ':', style={'margin-top': '10px', 'margin-bottom': '0px'}))
                col_result.append(html.P('Encounters: ' + str(value), style={'margin-bottom': '0px'}))
                col_result.append(html.P('Win/Loss: ' + str(win) + '-' + str(loss),style={'margin-bottom': '0px'}))
                col_result.append(html.P('Win % : ' + str(win/(win+loss)*100) + '%', style={'margin-bottom': '0px'}))
        result_layout.append(dbc.Col(children=col_result))

    return result_layout
