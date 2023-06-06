import plotly.express as px


def plot_portfolio_total(df,
                         theme,
                         skip_zero=True):
    account_names = df.account_name.unique().tolist()
    df = df.filter(regex='date|value')

    # remove all list_value's keep market_value's columns
    df = df.filter(regex='.*(?<!_list_value)$')
    df['total'] = df.sum(axis=1, numeric_only=True)

    if skip_zero:
        df = df.loc[:, (df.sum(axis=0) != 0.0)]

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


def plot_portfolio_all(df, theme, skip_zero=True):
    df.drop('account_name', axis=1, inplace=True)
    if skip_zero:
        df = df.loc[:, (df.sum(axis=0) != 0.0)]

    fig = px.line(df,
                  x=df.date,
                  y=df.columns,
                  title="All items",
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
