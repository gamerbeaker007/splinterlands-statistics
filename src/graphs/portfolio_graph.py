import plotly.express as px


def plot_portfolio_total(df,
                         theme,
                         skip_zero=True):
    account_names = df.account_name.tolist()
    df = df.groupby(['date'], as_index=False).sum()
    df = df.filter(regex='date|value')
    df['total'] = df.drop('collection_list_value', axis=1).sum(axis=1, numeric_only=True)

    if skip_zero:
        for column in df.columns.tolist():
            if df[column].sum() == 0.0:
                df.drop(columns=[column], inplace=True)

    fig = px.line(df,
                  x='date',
                  y=df.total,
                  title="Total portfolio values of '" + ",".join(account_names) + "' combined",
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
