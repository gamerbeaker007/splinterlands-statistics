import io
from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Input, Output, dcc, dash_table, State

from src.configuration import store
from src.graphs import land_resources_graph
from src.pages.land_resources_pages import land_resources_ids, land_resource_convert, land_region_page
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

layout = dbc.Container(
    [
        dcc.Store(id=land_resources_ids.land_resources_df),
        dcc.Store(id=land_resources_ids.land_resources_graph_settings),

        dbc.Row(
            children=[
                html.H3("Land Resources  "),
                land_resource_convert.layout,
                html.P("Tracking land resource prices"),
                dbc.Col(
                    dbc.Accordion(
                        children=[
                            dbc.AccordionItem(
                                children=[
                                    dbc.Checkbox(
                                        id=land_resources_ids.land_resources_checkbox_state,
                                        label="Log-y",
                                        value=False,
                                        className="dbc"
                                    ),
                                ],
                                title='Graph Settings',
                                className='dbc',
                            ),
                        ],
                        start_collapsed=True,
                        className='mb-3'
                    ),
                    width=3,
                ),
                dbc.Row(id=land_resources_ids.land_resources_container, className="dbc"),

                dbc.Accordion(
                    children=[
                        dbc.AccordionItem(
                            children=[
                                dbc.Row(
                                    id=land_resources_ids.land_resources_data_table,
                                    className='mb-3',
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Download CSV",
                                        id=land_resources_ids.land_download_btn_resources,
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
                ),
                land_region_page.layout,

            ],
            className='mb-3'),

        dcc.Download(id=land_resources_ids.land_download_dataframe_csv_resources)
    ])


@app.callback(
    Output(land_resources_ids.land_resources_checkbox_state, "children"),
    Output(land_resources_ids.land_resources_graph_settings, "data"),
    Input(land_resources_ids.land_resources_checkbox_state, "value"),
    State(land_resources_ids.land_resources_graph_settings, "data")
)
def checkbox(checked, graph_settings):
    if not graph_settings:
        graph_settings = {'log-y': checked}
    else:
        graph_settings['log-y'] = checked
    return str(checked), graph_settings


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
    Output(land_resources_ids.land_resources_container, 'children'),
    Input(land_resources_ids.land_resources_df, 'data'),
    Input(land_resources_ids.land_resources_graph_settings, "data"),
    Input(nav_ids.theme_store, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def update_container(data, graph_settings, theme):
    if not data or not graph_settings:
        return chart_util.blank_fig(theme)
    else:
        log_y = graph_settings['log-y']
        df = pd.read_json(StringIO(data), orient='split')
        return dbc.Row(children=[
            html.P("Below a char that represent how much resources you will receive for 1000 DEC (1$)"),
            dcc.Graph(
                figure=land_resources_graph.create_land_resources_dec_graph(df, log_y, theme),
                className='mb-3',
            ),
            html.P("Below a chart that represent how much it cost (DEC) to get 1000 of the resource."),
            dcc.Graph(
                figure=land_resources_graph.create_land_resources_graph(df, log_y, theme),
                className='mb-3',
            ),
            html.P([
                "Below a chart that represent what the factor is against grain based on the whitepaper", html.Br(),
                "Grain: 0.02", html.Br(),
                "Wood:  0.005  1 Wood  = 4  Grain", html.Br(),
                "Stone: 0.002  1 Stone = 10 Grain", html.Br(),
                "Iron:  0.0005 1 Iron  = 40 Grain"
            ]
            ),
            dcc.Graph(
                figure=land_resources_graph.create_land_resources_factor_graph(df, log_y, theme),
                className='mb-3',
            ),

        ], className="dbc")


@app.callback(
    Output(land_resources_ids.land_resources_data_table, 'children'),
    Input(land_resources_ids.land_resources_df, 'data'),
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
    Output(land_resources_ids.land_download_btn_resources, "data"),
    Input(land_resources_ids.land_download_dataframe_csv_resources, "n_clicks"),
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
