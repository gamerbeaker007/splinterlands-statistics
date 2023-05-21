import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

from main import app
from src import analyse
from src.static import static_values_enum
from src.static.static_values_enum import MatchType
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.Center(html.H1("Nemesis, ranked matches")),
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
    ])
])


@app.callback(
    Output('nemesis', 'children'),
    Input('dropdown-user-selection', 'value'),
    Input('dropdown-match-type-selection', 'value'),
)
def nemesis(account, filter_match_type):
    df = analyse.get_top_3_losing_account(account, filter_match_type)
    if not df.empty:
        li = []
        for index, row in df.iterrows():
            li.append(html.Li(str(row.opponent) + " (" + str(row.battle_id) + ")"))

        return html.Div(children=[html.Ul(children=li)])
    else:
        return html.Div("NA")
