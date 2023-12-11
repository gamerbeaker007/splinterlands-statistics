import plotly.express as px


def plot_land_all(land_df, theme):
    land_df.sort_values('created_date', inplace=True)

    fig = px.bar(land_df,
                  x='created_date',
                  y='received_amount',
                  color='resource_symbol',
                  barmode='group',
                  title='Total land values of')
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig
