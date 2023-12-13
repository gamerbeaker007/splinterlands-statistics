import plotly.express as px


def plot_land_all(land_df, theme):
    land_df.sort_values('created_date', inplace=True)

    fig = px.bar(land_df,
                 x='created_date',
                 y='received_amount',
                 color='resource_symbol',
                 barmode='group',
                 title='Total land values of: ' + str(land_df.player.unique()[0]),
                 labels={
                     "received_amount": "Received amount (log)",
                     "created_date": "Harvest date",
                     "resource_symbol": "Resource"
                 },
                 log_y=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig


def plot_cumsum(land_df, theme):
    # Calculate the difference between resource_amount and tax_amount
    land_df['amount_difference'] = land_df['resource_amount'] - land_df['tax_amount'] - land_df['grain_eaten'] - \
                                   land_df['grain_rewards_eaten']

    # Experiment to get correct grain amount
    # On one day received amount - tax.
    # For grain received minus consumed grain by other harvest
    temp_df = land_df.pivot(index='created_date', columns='resource_symbol',
                            values=['received_amount', 'grain_eaten', 'grain_rewards_eaten', 'resource_amount',
                                    'tax_amount'])
    temp_df['SPS_earned'] = temp_df[('resource_amount', 'SPS')] - temp_df[('tax_amount', 'SPS')]
    temp_df['RESEARCH_earned'] = temp_df[('resource_amount', 'RESEARCH')] - temp_df[('tax_amount', 'RESEARCH')]
    temp_df['GRAIN_earned'] = (temp_df[('received_amount', 'GRAIN')]
                               - temp_df[('grain_eaten', 'SPS')]
                               - temp_df[('grain_eaten', 'RESEARCH')])

    # Calculate cumulative sum for each resource_symbol
    temp_df['sps_cumsum'] = temp_df['SPS_earned'].cumsum()
    temp_df['grain_cumsum'] = temp_df['GRAIN_earned'].cumsum()

    land_df['received_sum'] = land_df.groupby('resource_symbol')['received_amount'].cumsum()

    # Plot with Plotly Express
    fig = px.line(land_df,
                  x='created_date',
                  y='received_sum',
                  color='resource_symbol',
                  title='Cumulative Sum of received amount for Each Resource Symbol',
                  log_y=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),
    )
    return fig
