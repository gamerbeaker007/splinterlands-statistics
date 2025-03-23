import pandas as pd
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


def create_land_resources_factor_graph(df, log_y, theme):
    # Step 1: Create a lookup table for base GRAIN conversion ratios
    conversion_ratios = {
        'WOOD': 4,
        'STONE': 10,
        'IRON': 40
    }

    # Step 3: We'll create a date-to-grain-price map to use in calculations
    grain_prices = df[df['token_symbol'] == 'GRAIN'].set_index('date')['resource_price'].to_dict()

    # Step 4: Filter only rows of interest
    df_filtered = df[df['token_symbol'].isin(['WOOD', 'STONE', 'IRON'])].copy()

    # Step 5: Calculate grain_equivalent and factor
    def calculate_grain_equivalent_and_factor(row):
        grain_price = grain_prices.get(row['date'])
        if grain_price:
            grain_equiv = row['resource_price'] / grain_price
            factor = grain_equiv / conversion_ratios[row['token_symbol']]
            return pd.Series([grain_equiv, factor])
        else:
            return pd.Series([None, None])

    df_filtered[['grain_equivalent', 'factor']] = df_filtered.apply(calculate_grain_equivalent_and_factor, axis=1)

    # Step 6: Optional: round for better readability
    df_filtered['grain_equivalent'] = df_filtered['grain_equivalent'].round(3)
    df_filtered['factor'] = df_filtered['factor'].round(2)

    fig = px.line(
        df_filtered,
        x="date",
        y="factor",
        log_y=True if log_y else False,
        color="token_symbol",
        title="Grain factor",
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
