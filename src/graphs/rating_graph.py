import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots

from src.static import static_values_enum
from src.static.static_values_enum import RatingLevel
import plotly.graph_objects as go


def create_rating_graph(df, theme):
    fig = px.scatter(df, x='created_date', y='rating', color='account', template=theme, height=800)
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


def plot_daily_stats_battle(daily_df, theme):
    daily_df['win_pct'] = daily_df.apply(lambda row: (row.win / row.battles * 100), axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    trace3 = go.Scatter(x=daily_df.created_date,
                        y=daily_df.win_pct,
                        mode='lines+markers',
                        name='win percentage')
    trace4 = go.Scatter(x=daily_df.created_date,
                        y=daily_df.battles,
                        mode='lines+markers',
                        name='battles')
    trace5 = go.Scatter(x=daily_df.created_date,
                        y=daily_df.win,
                        mode='lines+markers',
                        name='win')
    trace6 = go.Scatter(x=daily_df.created_date,
                        y=daily_df.loss,
                        mode='lines+markers',
                        name='loss')
    fig.add_trace(trace3, secondary_y=True)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.add_trace(trace6)
    fig.update_xaxes(showgrid=True, gridwidth=1)  # , gridcolor=GRID_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1)  # , gridcolor=GRID_COLOR)

    fig.update_layout(
        template=theme,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
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
            overlaying='y',
            side='right',
            anchor='x2',
            range=[0, 100],
            title='win (%)'),
    )
    return fig

