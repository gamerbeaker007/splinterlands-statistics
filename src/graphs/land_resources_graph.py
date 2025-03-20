import plotly.express as px


def create_land_resources_graph(df, theme):
    df = df.copy()  # Create a copy of the DataFrame
    fig = px.line(
        df,
        x="date",
        y="dec_price",
        color="token_symbol",
        title="DEC Price per Token Symbol",
        labels={"dec_price": "DEC Price", "date": "Date"},
        hover_data=["token_symbol", "dec_price"],
        template=theme,
        height=800,
    )

    return fig
