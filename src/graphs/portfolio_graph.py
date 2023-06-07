import pandas as pd
import plotly.express as px


def plot_portfolio_total(portfolio_df,
                         investments_df,
                         account_names,
                         theme):
    portfolio_df = portfolio_df.filter(regex='date|value')
    # remove all list_value's keep market_value's columns
    portfolio_df = portfolio_df.filter(regex='.*(?<!_list_value)$')
    portfolio_df.date = pd.to_datetime(portfolio_df.date)
    portfolio_df['Value'] = portfolio_df.sum(axis=1, numeric_only=True)

    temp_df = portfolio_df[['date', 'Value']]

    if not investments_df.empty:
        investments_df.date = pd.to_datetime(investments_df.date)
        investments_df.sort_values('date', inplace=True)
        investments_df['total_sum'] = investments_df.sum(axis=1, numeric_only=True)
        investments_df['Investment'] = investments_df.total_sum.cumsum()
        temp_df = temp_df.merge(investments_df[['date', 'Investment']], on='date', how='outer')

        # fig2 = px.line(investments_df,
        #                x='date',
        #                y=investments_df.total,
        #                markers=True)
        # fig2.update_traces(line_color='Red', name="Investment")
        #
        # fig.add_trace(fig2.data[0])
    temp_df.sort_values('date', inplace=True)
    fig = px.line(temp_df,
                  x='date',
                  y=temp_df.columns,
                  title="Total portfolio values of '" + ",".join(account_names) + "' combined",
                  markers=True)
    # fig.update_traces(line_color='Blue', name="Value")
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=portfolio_df.date,
        ),

    )
    return fig


def plot_portfolio_all(df, theme, skip_zero=True):
    df.drop('account_name', axis=1, inplace=True)

    if skip_zero:
        df = df.loc[:, (df.sum(axis=0) != 0.0)]

    df = df.sort_values('date')

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
