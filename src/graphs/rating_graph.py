import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

from src.static import static_values_enum
from src.static.static_values_enum import RatingLevel, Format
import plotly.graph_objects as go


def create_rating_graph(df, theme):
    df = df.copy()  # Create a copy of the DataFrame
    df['date'] = pd.to_datetime(df['created_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    fig = px.scatter(df, x='date', y='rating', color='account', template=theme, height=800)

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

    fig = make_subplots(specs=[[{"secondary_y": True}, {"secondary_y": True}]],
                        subplot_titles=("Modern", "Wild"),
                        rows=1,
                        cols=2)
    modern_pct = get_scatter_trace(modern_daily_df, 'win_pct', show_legend=True)
    modern_battles = get_scatter_trace(modern_daily_df, 'battles', show_legend=True)
    modern_win = get_scatter_trace(modern_daily_df, 'win', show_legend=True)
    modern_loss = get_scatter_trace(modern_daily_df, 'loss', show_legend=True)

    wild_pct = get_scatter_trace(wild_daily_df, 'win_pct')
    wild_battles = get_scatter_trace(wild_daily_df, 'battles')
    wild_win = get_scatter_trace(wild_daily_df, 'win')
    wild_loss = get_scatter_trace(wild_daily_df, 'loss')

    fig.add_trace(modern_pct, secondary_y=True, row=1, col=1)
    fig.add_trace(modern_battles, row=1, col=1)
    fig.add_trace(modern_win, row=1, col=1)
    fig.add_trace(modern_loss, row=1, col=1)
    fig.add_trace(wild_pct, secondary_y=True, row=1, col=2)
    fig.add_trace(wild_battles, row=1, col=2)
    fig.add_trace(wild_win, row=1, col=2)
    fig.add_trace(wild_loss, row=1, col=2)

    fig.update_xaxes(showgrid=True, gridwidth=0.5)
    fig.update_yaxes(showgrid=True, gridwidth=0.5)

    fig.update_layout(
        xaxis={'type': 'category', 'categoryorder': 'category ascending'},
        xaxis2={'type': 'category', 'categoryorder': 'category ascending'},
        template=theme,
        title_text="Daily battle stats",
        # legend=dict(
        #     orientation="h",
        #     yanchor="bottom",
        #     y=1.02,
        #     xanchor="right",
        #     x=1
        # ),
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
