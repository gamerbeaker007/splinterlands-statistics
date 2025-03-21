import plotly.express as px


def create_land_resources_dec_graph(df, theme):
    df = df.copy()
    df['dec_price'] = df['dec_price'] * 1000

    fig = px.line(
        df,
        x="date",
        y="dec_price",
        color="token_symbol",
        title="DEC 1000 (1$)",
        labels={"dec_price": "DEC Price", "date": "Date"},
        hover_data=["token_symbol", "dec_price"],
        template=theme,
        height=600,
    )

    return fig

def create_land_resources_graph(df, theme):
    df = df.copy()
    df['resource_price'] = df['resource_price'] * 1000
    fig = px.line(
        df,
        x="date",
        y="resource_price",
        color="token_symbol",
        title="Resource (1000) ",
        labels={"dec_price": "DEC Price", "date": "Date"},
        hover_data=["token_symbol", "dec_price"],
        template=theme,
        height=600,
    )

    return fig
