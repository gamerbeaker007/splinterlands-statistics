import numpy as np
import plotly.express as px

from src.static import static_values_enum
from src.static.static_values_enum import RatingLevel


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
