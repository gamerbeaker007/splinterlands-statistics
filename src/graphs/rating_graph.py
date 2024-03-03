import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.static import static_values_enum
from src.static.static_values_enum import RatingLevel, Format


def create_rating_graph(df, theme):
    df = df.copy()  # Create a copy of the DataFrame
    df['date'] = pd.to_datetime(df['created_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    fig = px.scatter(
        df,
        x='date',
        y='rating',
        color='account',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template=theme,
        height=800,
    )
    fig.update_layout(
        xaxis={'type': 'category', 'categoryorder': 'category ascending'},
    )

    # Start from 1 skip Novice
    for i in np.arange(1, len(static_values_enum.league_ratings)):
        y = static_values_enum.league_ratings[i]
        color = static_values_enum.league_colors[i]
        league_name = RatingLevel(i).name

        fig.add_hline(y=y,
                      line_width=1,
                      line_dash="dash",
                      annotation_text=league_name,
                      annotation_position="top left",
                      line_color=color)
    return fig


def get_scatter_trace(df, name, show_legend=False):
    color = {
        'win_pct': px.colors.qualitative.Plotly[0],
        'battles': px.colors.qualitative.Plotly[1],
        'win': px.colors.qualitative.Plotly[2],
        'loss': px.colors.qualitative.Plotly[3],
    }

    df = df.copy()  # Create a copy of the DataFrame
    df['date'] = pd.to_datetime(df['created_date']).dt.strftime('%Y-%m-%d')
    return go.Scatter(x=df.date,
                      y=df[name],
                      mode='lines+markers',
                      name=name,
                      legendgroup=name,
                      line=dict(
                          color=color[name],
                      ),
                      showlegend=show_legend
                      )


def plot_daily_stats_battle(daily_df, theme):
    daily_df['win_pct'] = daily_df.apply(lambda row: (row.win / row.battles * 100), axis=1)

    wild_daily_df = daily_df.loc[daily_df['format'] == Format.wild.value]
    modern_daily_df = daily_df.loc[daily_df['format'] == Format.modern.value]

    fig = make_subplots(
        specs=[[{"secondary_y": True}, {"secondary_y": True}]],
        subplot_titles=("Modern", "Wild"),
        horizontal_spacing=0.1,
        rows=1,
        cols=2,
    )

    # Get all columns except 'created_date' and 'format'
    columns_to_plot = modern_daily_df.columns.difference(['created_date', 'format'])
    for column in columns_to_plot:
        if column == 'win_pct':
            secondary_y = True
        else:
            secondary_y = False
        fig.add_trace(
            get_scatter_trace(modern_daily_df, column, show_legend=False),
            secondary_y=secondary_y,
            row=1,
            col=1
        )

    columns_to_plot = wild_daily_df.columns.difference(['created_date', 'format'])
    for column in columns_to_plot:
        if column == 'win_pct':
            secondary_y = True
        else:
            secondary_y = False
        fig.add_trace(
            get_scatter_trace(wild_daily_df, column, show_legend=True),
            secondary_y=secondary_y,
            row=1,
            col=2
        )

    fig.update_xaxes(showgrid=True, gridwidth=0.5)
    fig.update_yaxes(showgrid=True, gridwidth=0.5)

    fig.update_layout(
        xaxis={'type': 'category', 'categoryorder': 'category ascending'},
        xaxis2={'type': 'category', 'categoryorder': 'category ascending'},
        template=theme,
        title_text="Daily battle stats",
        margin=dict(l=10, r=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,
            xanchor="right",
            x=1
        ),
        yaxis1=dict(
            showgrid=False,
            range=[0, daily_df.battles.max() + 20],
            title="battles",
        ),
        yaxis2=dict(
            showgrid=False,
            range=[0, 100],
            title='win (%)'),

        yaxis3=dict(
            showgrid=False,
            range=[0, daily_df.battles.max() + 20],
            title="battles",
        ),
        yaxis4=dict(
            showgrid=False,
            range=[0, 100],
            title='win (%)'),
    )
    return fig
