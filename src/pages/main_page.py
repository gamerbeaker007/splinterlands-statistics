import logging

from dash import html, callback, Output, Input, dash_table, dcc
import dash_bootstrap_components as dbc
from src import analyse
from src.configuration import config
from src.static import static_values_enum
from src.static.static_values_enum import MatchType, CardType

layout = dbc.Container([
    dbc.Row([
        html.H1('Battle Statistics '),
        dbc.Col(html.P('Filter on')),
        dbc.Col(dcc.Dropdown(options=['ALL'] + config.account_names,
                             value='ALL',
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
        dbc.Col(dcc.Dropdown(options=['ALL'] + static_values_enum.get_list_of_enum(CardType),
                             value='ALL',
                             id='dropdown-type-selection',
                             className='dbc')),
        dbc.Col(dcc.Dropdown(options=['ALL'] + static_values_enum.get_list_of_enum(MatchType),
                             value='ALL',
                             id='dropdown-match-type-selection',
                             className='dbc'))
    ]),
    dbc.Row([
        html.Div(id="battle-count", className="dbc"),
    ]),
    dbc.Row([
        html.Div(id="table", className="dbc"),
    ]),
])


@callback(
    Output('table', 'children'),
    Input('dropdown-type-selection', 'value'),
    Input('dropdown-user-selection', 'value'),
    Input('dropdown-match-type-selection', 'value')
)
def update_table(filter_type, filter_user, filter_match_type):
    logging.info('Update table...')

    # if ALL filter None :)
    if filter_user == 'ALL':
        filter_user = None
    if filter_type == 'ALL':
        filter_type = None
    if filter_match_type == 'ALL':
        filter_match_type = None

    df = analyse.get_losing_df(filter_account=filter_user, filter_match_type=filter_match_type, filter_type=filter_type)

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        row_selectable=False,
        row_deletable=False,
        editable=False,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        page_size=10,
    ),


@callback(
    Output('battle-count', 'children'),
    Input('dropdown-type-selection', 'value'),
    Input('dropdown-user-selection', 'value'),
    Input('dropdown-match-type-selection', 'value')
)
def battle_count(filter_type, filter_user, filter_match_type):
    logging.info('Update battle count...')

    # if ALL filter None :)
    if filter_user == 'ALL':
        filter_user = None
    if filter_type == 'ALL':
        filter_type = None
    if filter_match_type == 'ALL':
        filter_match_type = None

    bc = analyse.get_battles_df(filter_account=filter_user, filter_match_type=filter_match_type,
                                filter_type=filter_type)
    return html.Div("Battle count: " + str(bc))
