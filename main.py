import logging
import os

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, html, callback, Output, Input, dash_table, dcc

from src import analyse
from src import battle_store, collection_store
from src.configuration import store, config
from src.static import static_values_enum
from src.static.static_values_enum import MatchType, CardType

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])


def load_stores():
    if os.path.isfile(store.collection_file):
        store.collection_df = pd.read_csv(store.collection_file, index_col=[0]).sort_index()

    if os.path.isfile(store.battle_file):
        store.battle_df = pd.read_csv(store.battle_file, index_col=0)
        store.battle_df = store.battle_df.where(store.battle_df.notnull(), None)
    # else:
    #     store.battle_df = pd.DataFrame(columns=['uid', 'match_type', 'format', 'win', 'loss'])

    if os.path.isfile(store.last_processed_file):
        store.last_processed_df = pd.read_csv(store.last_processed_file, index_col=0)
    # else:
    #     store.last_processed_df = pd.DataFrame(columns=['account', 'last_processed'])

    if os.path.isfile(store.battle_big_file):
        store.battle_big_df = pd.read_csv(store.battle_big_file, index_col=0)

    if os.path.isfile(store.rating_file):
        store.rating_df = pd.read_csv(store.rating_file, index_col=0)

    if os.path.isfile(store.losing_big_file):
        store.losing_big_df = pd.read_csv(store.losing_big_file, index_col=0)


def save_stores():
    store.last_processed_df.sort_index().to_csv(store.last_processed_file)
    store.battle_df.sort_index().to_csv(store.battle_file)
    store.collection_df.sort_index().to_csv(store.collection_file)
    store.battle_big_df.sort_index().to_csv(store.battle_big_file)
    store.rating_df.sort_index().to_csv(store.rating_file)
    store.losing_big_df.sort_index().to_csv(store.losing_big_file)


def main():
    load_stores()

    collection_store.update_collection()
    battle_store.process_battles()

    save_stores()

    app.run_server(debug=True)


app.layout = html.Div(children=[
    html.H1(children='Battle Statistics '),
    html.Div(children='My First App with Data'),
    html.P(children='Filter on'),
    dcc.Dropdown(options=config.account_names + ['ALL'],
                 value='ALL',
                 id='dropdown-user-selection',
                 className='dbc'),html.Br(),
    dcc.Dropdown(options=static_values_enum.get_list_of_enum(CardType) + ['ALL'],
                 value='ALL',
                 id='dropdown-type-selection',
                 className='dbc'),html.Br(),
    dcc.Dropdown(options=static_values_enum.get_list_of_enum(MatchType) + ['ALL'],
                 value='ALL',
                 id='dropdown-match-type-selection',
                 className='dbc'),html.Br(),
    html.Br(),

    html.Div(id="battle-count", className="dbc"),
    html.Br(), html.Br(), html.Br(), html.Br(),

    html.Div(id="table", className="dbc"),
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

    bc = analyse.get_battles_df(filter_account=filter_user, filter_match_type=filter_match_type, filter_type=filter_type)
    return html.Div("Battle count: " + str(bc))


if __name__ == '__main__':
    main()
