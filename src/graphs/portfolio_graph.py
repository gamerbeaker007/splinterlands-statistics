import plotly.express as px


def plot_portfolio_all(df,
                       theme,
                       skip_zero=True):
    df.drop(columns=['account_name'], inplace=True)

    if skip_zero:
        for column in df.columns.tolist():
            if df[column].sum() == 0.0:
                df.drop(columns=[column], inplace=True)

    fig = px.line(df,
                  x='date',
                  y=df.columns,
                  title='Portfolio',
                  markers=True)

    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=df.date,
        ),

    )
    return fig
