import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dash_table, dcc

from main import app
from src import analyse
from src.static.static_layout import *
from src.utils import store_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Statistics battles'),
        html.P('Your battle statistics of your summoners and monster'),
        dbc.Col(html.P('Filter on')),
        dbc.Col(dcc.Dropdown(store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
    ]),
    dbc.Row([
        dbc.Col(
            [
                html.H4("Filter Bar"),
                dbc.ButtonGroup([
                    dbc.Button(
                        id="water-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(water_filter_icon),
                                className="round-sm-img",
                            ),
                        ],
                    ),
                    dbc.Button(
                        id="death-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(death_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                    dbc.Button(
                        id="dragon-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(dragon_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                    dbc.Button(
                        id="life-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(life_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                    dbc.Button(
                        id="fire-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(fire_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                    dbc.Button(
                        id="earth-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(earth_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                    dbc.Button(
                        id="neutral-filter-button",
                        children=[
                            html.Img(
                                src=app.get_asset_url(neutral_filter_icon),
                                className="round-sm-img",
                            )

                        ],
                    ),
                ],)
            ],
            md=3,
            class_name="mb-4",
        ),
        dbc.Col(
            [
                html.Div(id="filter-output")
            ]
        )

    ]),
    dbc.Row([
        html.Div(id='main-table', className='dbc'),
    ]),
    dcc.Store(id='filtered-battle-df')

])


@app.callback(
    Output('main-table', 'children'),
    Input('filtered-battle-df', 'data'),
)
def update_main_table(filtered_df):
    filtered_df = pd.read_json(filtered_df, orient='split')

    if not filtered_df.empty:
        return dash_table.DataTable(
            # columns=[{'name': i, 'id': i} for i in df.columns],
            columns=[
                {'id': 'url', 'name': 'Card', 'presentation': 'markdown'},
                {'id': 'card_name', 'name': 'Name'},
                {'id': 'level', 'name': 'Level'},
                # {'id': 'win_to_loss_ratio', 'name': 'win_to_loss_ratio'},
                {'id': 'battles', 'name': 'Battles'},
                # {'id': 'win_ratio', 'name': 'win_ratio'},
                {'id': 'win_percentage', 'name': 'Win Percentage'},
            ],
            data=filtered_df.to_dict('records'),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action='native',
            sort_action='native',
            style_table={'overflowX': 'auto'},
            style_cell_conditional=[{'if': {'column_id': 'url'}, 'width': '200px'}, ],
            page_size=10,
        ),
    else:
        return dash_table.DataTable()


@app.callback(Output('filtered-battle-df', 'data'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              Input("water-filter-button", "n_clicks"),
              Input("death-filter-button", "n_clicks"),
              Input("life-filter-button", "n_clicks"),
              Input("fire-filter-button", "n_clicks"),
              Input("dragon-filter-button", "n_clicks"),
              Input("earth-filter-button", "n_clicks"),
              Input("neutral-filter-button", "n_clicks"),
              )
def filter_battle_df(account,
                     trigger_daily,
                     water_clicks,
                     death_clicks,
                     life_clicks,
                     fire_clicks,
                     dragon_clicks,
                     earth_clicks,
                     neutral_clicks):
    water_active = is_active(water_clicks)
    death_active = is_active(death_clicks)
    life_active = is_active(life_clicks)
    fire_active = is_active(fire_clicks)
    dragon_active = is_active(dragon_clicks)
    earth_active = is_active(earth_clicks)
    neutral_active = is_active(neutral_clicks)

    df = analyse.get_my_battles_df(account)
    df = analyse.filter_out_splinter(df,
                                     water_active,
                                     death_active,
                                     life_active,
                                     fire_active,
                                     dragon_active,
                                     earth_active,
                                     neutral_active)
    return df.to_json(date_format='iso', orient='split')


@app.callback(
    Output("water-filter-button", "class_name"),
    Input("water-filter-button", "n_clicks"),
)
def toggle_water_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("death-filter-button", "class_name"),
    Input("death-filter-button", "n_clicks"),

)
def toggle_death_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("life-filter-button", "class_name"),
    Input("life-filter-button", "n_clicks"),

)
def toggle_life_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("earth-filter-button", "class_name"),
    Input("earth-filter-button", "n_clicks"),

)
def toggle_earth_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("fire-filter-button", "class_name"),
    Input("fire-filter-button", "n_clicks"),

)
def toggle_fire_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("dragon-filter-button", "class_name"),
    Input("dragon-filter-button", "n_clicks"),

)
def toggle_dragon_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


@app.callback(
    Output("neutral-filter-button", "class_name"),
    Input("neutral-filter-button", "n_clicks"),

)
def toggle_neutral_filter(n_clicks):
    return btn_active if is_active(n_clicks) else btn_inactive


def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False
