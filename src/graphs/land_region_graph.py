import pandas as pd
import plotly.graph_objects as go


def create_land_region_active_graph(df, theme):
    df = df.copy()
    # Step 1: Convert date to datetime if needed
    df['date'] = pd.to_datetime(df['date'])

    # Step 2: Filter to the latest date
    latest_date = df['date'].max()
    latest_df = df[df['date'] == latest_date].copy()

    # Step 3: Calculate inactive column
    latest_df['inactive'] = 1000 - latest_df['active']

    # Step 4: Sort by active ascending
    latest_df = latest_df.sort_values(by='active', ascending=False)

    # Step 5: Create the stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name='Active', x=latest_df['region_uid'], y=latest_df['active']),
        go.Bar(name='Inactive', x=latest_df['region_uid'], y=latest_df['inactive'])
    ])

    # Update layout for stacking
    fig.update_layout(
        barmode='stack',
        title=f'Active vs Inactive Deeds per Region (as of {latest_date.date()})',
        xaxis_title='Region UID',
        yaxis_title='Power',
        xaxis_tickangle=45,
        legend=dict(x=0.85, y=0.95),
        template=theme,
    )
    return fig
