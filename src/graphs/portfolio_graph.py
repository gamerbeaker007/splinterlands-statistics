import plotly.express as px


def plot_portfolio_total(portfolio_df, combined_users, theme):
    portfolio_df.sort_values('date', inplace=True)
    if 'total_investment_value' in portfolio_df.columns.tolist():
        column_data = portfolio_df[['total_value', 'total_investment_value']].columns
    else:
        column_data = portfolio_df[['total_value']].columns

    fig = px.line(portfolio_df,
                  x='date',
                  y=column_data,
                  title="Total portfolio values of '" + ",".join(combined_users) + "' combined",
                  markers=True)
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig


def plot_portfolio_all(df, theme, skip_zero=True):
    temp_df = df.drop('account_name', axis=1)

    if skip_zero:
        temp_df = temp_df.drop('date', axis=1)
        temp_df = temp_df.loc[:, (temp_df.sum(axis=0) != 0.0)]
        temp_df['date'] = df[['date']]

    fig = px.line(temp_df,
                  x=temp_df.date,
                  y=temp_df.columns,
                  title="All items",
                  markers=True)
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
        ),

    )
    return fig
