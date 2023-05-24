import dash_bootstrap_components as dbc
from dash import html, Output, Input, dash_table, dcc

from main import app
from src import analyse
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics battles battles'),
        html.P('Your battle  statistics of your summoners and monster'),
        dbc.Col(html.P('Filter on')),
        dbc.Col(dcc.Dropdown(store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
    ]),
    dbc.Row([
        html.Div(id="main-table", className="dbc"),
    ]),
])


@app.callback(
    Output('main-table', 'children'),
    Input('dropdown-user-selection', 'value'),
)
def update_main_table(filter_user):

    df = analyse.get_my_battles_df(filter_user)
    if not df.empty:
        return dash_table.DataTable(
            # columns=[{"name": i, "id": i} for i in df.columns],
            columns=[
                {"id": "url", "name": "url", "presentation": "markdown"},
                {"id": "card_name", "name": "card_name"},
                {"id": "level", "name": "level"},
                # {"id": "win_to_loss_ratio", "name": "win_to_loss_ratio"},
                {"id": "battles", "name": "battles"},
                # {"id": "win_ratio", "name": "win_ratio"},
                {"id": "win_percentage", "name": "win_percentage"},
            ],
            data=df.to_dict("records"),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "auto"},
            style_cell_conditional=[{"if": {"column_id": "url"}, "width": "200px"}, ],
            page_size=10,
        ),
    else:
        return dash_table.DataTable()

