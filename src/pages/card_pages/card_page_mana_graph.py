import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Output, Input, dcc

from main import app
from src.configuration import config
from src.pages.card_pages import card_page_ids
from src.pages.navigation_pages import nav_ids
from src.utils import chart_util


layout = dbc.Row([
    dcc.Graph(id=card_page_ids.card_mana_cap_graph)
])


@app.callback(
    Output(card_page_ids.card_mana_cap_graph, 'figure'),
    Input(card_page_ids.filtered_cards_battle_df, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
def update_mana_cap_card_graph(filtered_df, theme):
    if not filtered_df:
        return "No card selected"

    filtered_df = pd.read_json(filtered_df, orient='split')
    fig = chart_util.blank_fig(theme)
    if not filtered_df.empty:
        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        # Create a new column 'bucket' and assign values to the corresponding bucket
        bucket_labels = [f"{start}-{end}" for start, end in zip(bins[:-1], bins[1:])]
        filtered_df['bucket'] = pd.cut(filtered_df['mana_cap'], bins, labels=bucket_labels, right=False)

        grouped_data = filtered_df.groupby(['bucket', 'card_name']).size().reset_index(name='count')
        fig = px.bar(grouped_data,
                     x='bucket',
                     y='count',
                     color='card_name',
                     height=200,
                     )
        fig.update_layout(template=theme,
                          showlegend=False,
                          margin=dict(l=10, r=20, t=20, b=10),
                          xaxis_title='Battle count per mana cap',
                          yaxis_title='',
                          )
    return fig
