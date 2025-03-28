import plotly.express as px

COLOR_MAP = {
    "GRAIN": "orange",
    "WOOD": "saddlebrown",  # a nice brown color name
    "STONE": "gray",
    "IRON": "olive"
}


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
        color_discrete_map=COLOR_MAP,
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
        color_discrete_map=COLOR_MAP,
        labels={"resource_price_1000": "Cost in DEC", "date": "Date"},
        hover_data=["token_symbol", "resource_price_1000"],
        template=theme,
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    return fig


def create_land_resources_factor_graph(df, log_y, theme):
    df['grain_equivalent'] = df['grain_equivalent'].round(3)
    df['factor'] = df['factor'].round(2)
    df_filtered = df[df['token_symbol'].isin(['WOOD', 'STONE', 'IRON'])].copy()

    fig = px.line(
        df_filtered,
        x="date",
        y="factor",
        log_y=True if log_y else False,
        color="token_symbol",
        title="Grain factor",
        color_discrete_map=COLOR_MAP,
        labels={"factor": "Factor", "date": "Date"},
        hover_data=["token_symbol", "factor"],
        template=theme,
        height=600,
    )
    fig.add_hline(
        y=1.00,
        line_dash="dash",
        line_color="gray",
        annotation_text="1.00 (Grain baseline)",
        annotation_position="top left"
    )

    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    return fig
