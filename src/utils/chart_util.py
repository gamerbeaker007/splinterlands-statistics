import plotly.express as px


def blank_fig(theme):
    fig = px.scatter()
    fig.update_layout(template=theme,
                      margin=dict(l=10, r=10, t=10, b=10),
                      )
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig
