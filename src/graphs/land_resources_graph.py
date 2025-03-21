import plotly.express as px


def create_land_resources_dec_graph(df, log_y, theme):
    df = df.copy()
    df['dec_price_1000'] = df['dec_price'] * 1000

    fig = px.line(
        df,
        x="date",
        y="dec_price_1000",
        log_y=True if log_y else False,
        color="token_symbol",
        title="1000 DEC",
        labels={"dec_price_1000": "Amount of Resource", "date": "Date"},
        hover_data=["token_symbol", "dec_price_1000"],
        template=theme,
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    return fig


def create_land_resources_graph(df, log_y, theme):
    df = df.copy()
    df['resource_price_1000'] = df['resource_price'] * 1000
    fig = px.line(
        df,
        x="date",
        y="resource_price_1000",
        log_y=True if log_y else False,
        color="token_symbol",
        title="1000 Resources",
        labels={"resource_price_1000": "Cost in DEC", "date": "Date"},
        hover_data=["token_symbol", "resource_price_1000"],
        template=theme,
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    return fig
