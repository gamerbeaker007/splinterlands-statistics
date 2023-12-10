import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc, ctx

from main import app
from src.pages.land import land_ids
from src.pages.navigation_pages import nav_ids
from src.utils import store_util

layout = dbc.Container([
    dcc.Store(id=land_ids.filtered_land_df),

    dbc.Row([
        html.H1('Land'),
        dbc.Col(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Account'),
                    dcc.Dropdown(id=land_ids.dropdown_user_selection_land,
                                 className='dbc',
                                 style={'width': '70%'},
                                 ),

                ],
                className='mb-3',
            ),
            md=4,
        ),
    ]),
    # dbc.Row(dcc.Graph(id=land_ids.total_all_portfolio_graph), className='mb-3'),
])


@app.callback(Output(land_ids.dropdown_user_selection_land, 'value'),
              Output(land_ids.dropdown_user_selection_land, 'options'),
              Input(nav_ids.trigger_daily, 'data'),
              )
def update_user_list(tigger):
    return store_util.get_first_account_name(), store_util.get_account_names()


@app.callback(Output(land_ids.filtered_land_df, 'data'),
              Input(land_ids.dropdown_user_selection_land, 'value'),
              )
def update_filter_data(account):
    print("Trigger id: " + str(ctx.triggered_id))


# @app.callback(Output(portfolio_ids.total_all_portfolio_graph, 'figure'),
#               Input(portfolio_ids.filtered_portfolio_df, 'data'),
#               Input(portfolio_ids.dropdown_user_selection_portfolio, 'value'),
#               Input(nav_ids.theme_store, 'data'),
#               )
# def update_portfolio_total_graph(filtered_df, combined_users, theme):
#
