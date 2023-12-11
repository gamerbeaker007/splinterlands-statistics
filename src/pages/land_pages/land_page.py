import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dcc, ctx

from main import app
from src.configuration import store
from src.graphs import land_graph
from src.pages.land_pages import land_ids
from src.pages.navigation_pages import nav_ids
from src.utils import store_util, chart_util

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
    dbc.Row(dcc.Graph(id=land_ids.all_graph), className='mb-3'),
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
    if not store.land.empty:
        # Filter before processing is done
        df = store.land.loc[(store.land.player == account)].copy()
        df.created_date = pd.to_datetime(df.created_date)
        columns = ['received_amount', 'grain_eaten', 'grain_rewards_eaten', 'resource_amount', 'tax_amount']
        temp_df = df.groupby([df.created_date.dt.date, df.resource_symbol])[columns].sum().reset_index()
        # temp_df = temp_df.pivot(index='created_date', columns='resource_symbol', values=columns)

        return temp_df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(Output(land_ids.all_graph, 'figure'),
              Input(land_ids.filtered_land_df, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_land_total_graph(filtered_df, theme):

    if not filtered_df:
        return chart_util.blank_fig(theme)
    else:
        temp_df = pd.read_json(filtered_df, orient='split')

    if temp_df.empty:
        return chart_util.blank_fig(theme)
    else:
        return land_graph.plot_land_all(temp_df, theme)

