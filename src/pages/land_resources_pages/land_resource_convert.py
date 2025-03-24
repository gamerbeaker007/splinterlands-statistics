import datetime
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Input, Output, dcc, State
from dash.exceptions import PreventUpdate

from src.api import spl
from src.pages.main_dash import app
from src.static.static_values_enum import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, dec_icon_url, \
    sps_icon_url
from src.utils.trace_logging import measure_duration

default_width = '150px'
plus_style = {"fontSize": "32px", "text-align": "center"}
transaction_fee = 0.90  # 10% conversion fee is charged


# Helper function to load images
def resource_column(resource, icon_url, label=False):
    return dbc.Row([
        html.Img(src=f"{icon_url}", width=default_width),
        dbc.Input(id=f"input_{resource.lower()}",
                  type="number",
                  min=0,
                  placeholder=f"{resource}",
                  className="m-1 border border-dark"),
    ], className="dbc") if not label else dbc.Row([
        html.Img(src=f"{icon_url}",
                 width=default_width),
        html.Div(id=f"label_{resource.lower()}", children="0", style={"fontWeight": "bold"})
    ])


layout = dbc.Container([
    # Stores for metrics and prices
    dcc.Store(id="store_metrics"),
    dcc.Store(id="store_prices"),

    # Info text
    html.Div(id="info_text", className="dbc"),

    # Row of 8 columns
    dbc.Row([
        dbc.Col(resource_column("GRAIN", grain_icon_url)),
        dbc.Col(html.Div("+", style=plus_style)),
        dbc.Col(resource_column("WOOD", wood_icon_url)),
        dbc.Col(html.Div("+", style=plus_style)),
        dbc.Col(resource_column("STONE", stone_icon_url)),
        dbc.Col(html.Div("+", style=plus_style)),
        dbc.Col(resource_column("IRON", iron_icon_url)),
        dbc.Col(html.Div("=", style=plus_style)),
        dbc.Col(html.Div([
            resource_column("DEC", dec_icon_url, label=True),
            resource_column("SPS", sps_icon_url, label=True),
        ])),
    ], align="center", className="g-2"),
])


# Callback to populate info text and store data
@app.callback(
    Output("info_text", "children"),
    Output("store_metrics", "data"),
    Output("store_prices", "data"),
    Input("info_text", "id"),  # Triggers on page load
)
@measure_duration
def update_info_text(_):
    metrics = spl.get_land_resources_pools()
    prices = pd.DataFrame(spl.get_prices(), index=[0])
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = html.P(["Convert your resources to see the current DEC/SPS current prices is.",
                  html.Br(),
                  f"Based on the market prices of {time_stamp}"])
    return text, metrics.to_json(date_format='iso', orient='split'), prices.to_json(date_format='iso', orient='split')


# Callback to calculate output when any input changes
@app.callback(
    Output("label_dec", "children"),
    Output("label_sps", "children"),
    Input("input_grain", "value"),
    Input("input_wood", "value"),
    Input("input_stone", "value"),
    Input("input_iron", "value"),
    State("store_metrics", "data"),
    State("store_prices", "data"),
    prevent_initial_call=True,
)
@measure_duration
def calculate_values(grain, wood, stone, iron, metrics, prices):
    if not metrics or not prices:
        raise PreventUpdate
    metrics = pd.read_json(StringIO(metrics), orient='split')
    prices = pd.read_json(StringIO(prices), orient='split')

    # Replace with your real calculation logic
    grain = grain or 0
    wood = wood or 0
    stone = stone or 0
    iron = iron or 0

    total_dec_amount = (
            (grain / metrics[metrics['token_symbol'] == 'GRAIN']['dec_price'].values[0]) * transaction_fee +
            (wood / metrics[metrics['token_symbol'] == 'WOOD']['dec_price'].values[0]) * transaction_fee +
            (stone / metrics[metrics['token_symbol'] == 'STONE']['dec_price'].values[0]) * transaction_fee +
            (iron / metrics[metrics['token_symbol'] == 'IRON']['dec_price'].values[0]) * transaction_fee
    )

    # Value of 1000 DEC in USD
    usd_value = total_dec_amount * prices['dec'].values[0]
    sps_amount = usd_value / prices['sps'].values[0]

    return f"{total_dec_amount:.2f} DEC", f"{sps_amount:.2f} SPS"
