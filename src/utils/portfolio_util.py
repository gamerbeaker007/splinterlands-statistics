import pandas as pd
from dateutil import parser

from src.configuration import store
from src.utils import store_util


def update_investment(account, amount, my_date):
    df = store.portfolio_investments.copy()
    df.date = pd.to_datetime(df.date)
    my_date = parser.parse(my_date)
    if df.empty or df.loc[(df.date == my_date) & (df.account_name == account)].empty:
        new_df = pd.DataFrame({'date': pd.to_datetime(my_date),
                               'account_name': account,
                               'amount': amount},
                              index=[0])
        # new_df.date = new_df.date.dt.date
        df = pd.concat([df, new_df], ignore_index=True)

    else:
        df.loc[
            (df.date == my_date) &
            (df.account_name == account), 'amount'] += amount
    store.portfolio_investments = df
    store_util.save_stores()
