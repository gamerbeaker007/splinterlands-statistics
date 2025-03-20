import io
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Input, Output, dcc, dash_table, State

from src.configuration import store
from src.graphs import land_resources_graph
from src.pages.land_resources_pages import land_resources_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

layout = dbc.Container(
    [
        dcc.Store(id=land_resources_ids.land_resources_df),

        dbc.Row(
            children=[
                html.H3("Land Resources  "),
                html.P("Tracking land resource prices"),
                dcc.Graph(
                    id=land_resources_ids.land_resources_graph,
                    className='mb-3',
                ),
                dbc.Accordion(
                    children=[
                        dbc.AccordionItem(
                            children=[
                                dbc.Row(
                                    id=land_resources_ids.land_resources_data_table,
                                    className='mb-3',
                                ),
                                dbc.Row(
                                    dbc.Button(
                                        "Download CSV",
                                        id="download-btn",
                                        color="primary",
                                        className="mb-3"
                                    ),
                                    className='mb-3',
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

        dcc.Download(id="download-dataframe-csv")
    ])


@app.callback(
    Output(land_resources_ids.land_resources_df, 'data'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_df(trigger):
    if not store.land_resources.empty:
        # Filter before processing is done
        df = store.land_resources.copy()
        df.created_date = pd.to_datetime(df.created_date)
        return df.to_json(date_format='iso', orient='split')
    else:
        return None


@app.callback(
    Output(land_resources_ids.land_resources_graph, 'figure'),
    Input(land_resources_ids.land_resources_df, 'data'),
    Input(nav_ids.theme_store, 'data'),

)
@measure_duration
def update_container(data, theme):
    if not data:
        return chart_util.blank_fig(theme)
    else:
        df = pd.read_json(StringIO(data), orient='split')
        return land_resources_graph.create_land_resources_graph(df, theme)


@app.callback(
    Output(land_resources_ids.land_resources_data_table, 'children'),
    Input(land_resources_ids.land_resources_df, 'data'),
)
@measure_duration
def update_container(data):
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
            # style_cell_conditional=[{'if': {'column_id': 'url'}, 'width': '200px'}, ],
            page_size=10,
        )


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    State(land_resources_ids.land_resources_df, 'data'),
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
        return dict(content=csv_buffer.getvalue(), filename="land_resources.csv")
