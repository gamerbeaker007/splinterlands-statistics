import io
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, dcc, dash_table, State, html

from src.configuration import store
from src.graphs import land_region_graph
from src.pages.land_resources_pages import land_resources_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

layout = dbc.Container(
    [
        dcc.Store(id=land_resources_ids.land_region_df),

        dbc.Row(
            children=[
                html.H3("Tracking land region"),
                dbc.Row(id=land_resources_ids.land_region_container, className="dbc"),
                dbc.Accordion(
                    children=[
                        dbc.AccordionItem(
                            children=[
                                dbc.Row(
                                    id=land_resources_ids.land_region_data_table,
                                    className='mb-3',
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Download CSV",
                                        id=land_resources_ids.land_download_btn_region,
                                        color="primary",
                                        className="mb-3"
                                    ),
                                    className='mb-3',
                                    width=3,
                                ),
                            ],
                            title='Data',
                            className='dbc',
                        ),
                    ],
                    start_collapsed=True,
                    className='mb-3'
                )
            ],
            className='mb-3'),

        dcc.Download(id=land_resources_ids.land_download_dataframe_csv_region)
    ])


@app.callback(
    Output(land_resources_ids.land_region_df, 'data'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_df(trigger):
    if not store.land_region.empty:
        # Filter before processing is done
        df = store.land_region.copy()
        df.date = pd.to_datetime(df.date)
        return df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(
    Output(land_resources_ids.land_region_data_table, 'children'),
    Input(land_resources_ids.land_region_df, 'data'),
)
@measure_duration
def update_data_table(data):
    if not data:
        return None
    else:
        df = pd.read_json(StringIO(data), orient='split')
        return dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action='native',
            sort_action='native',
            style_table={'overflowX': 'auto'},
            page_size=10,
        )


@app.callback(
    Output(land_resources_ids.land_download_dataframe_csv_region, "data"),
    Input(land_resources_ids.land_download_btn_region, "n_clicks"),
    State(land_resources_ids.land_region_df, 'data'),
    prevent_initial_call=True
)
def download_csv(n_clicks, data):
    if not data:
        return None
    else:
        df = pd.read_json(StringIO(data), orient='split')
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return dict(content=csv_buffer.getvalue(), filename="land_region.csv")


@app.callback(
    Output(land_resources_ids.land_region_container, 'children'),
    Input(land_resources_ids.land_region_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def update_container(data, theme):
    if not data:
        return chart_util.blank_fig(theme)
    else:
        df = pd.read_json(StringIO(data), orient='split')
        return dbc.Row(children=[
            html.P("Below a chart with active/inactive deed "),
            dcc.Graph(
                figure=land_region_graph.create_land_region_active_graph(df, theme),
                className='mb-3',
            ),
        ], className="dbc")
