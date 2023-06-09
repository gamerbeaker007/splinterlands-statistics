import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output

from main import app
from src import analyse
from src.static import static_values_enum
from src.static.static_values_enum import MatchType
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.Center(html.H1('Nemesis, ranked matches')),
        dbc.Col(dcc.Dropdown(options=store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        dbc.Col(dcc.Dropdown(options=['ALL'] + static_values_enum.get_list_of_enum(MatchType),
                             value='ALL',
                             id='dropdown-match-type-selection',
                             className='dbc')),
        html.Hr(),
        html.Br(),
        html.P('Your nemesis:'),
        html.Div(id='nemesis'),
        html.Hr(),
        dcc.Store(id='filtered-nemesis-df'),

    ])
])


@app.callback(
    Output('nemesis', 'children'),
    Input('filtered-nemesis-df', 'data'),
)
def nemesis(filtered_df):
    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        li = []
        for index, row in filtered_df.iterrows():
            li.append(html.Li(str(row.opponent) + ' (' + str(row.battle_id) + ')'))

        return html.Div(children=[html.Ul(children=li)])
    else:
        return html.Div('NA')


@app.callback(Output('filtered-nemesis-df', 'data'),
              Input('dropdown-user-selection', 'value'),
              Input('dropdown-match-type-selection', 'value'),
              )
def filter_rating_df(account, filter_match_type):
    df = analyse.get_top_3_losing_account(account, filter_match_type)
    return df.to_json(date_format='iso', orient='split')
