import logging
from datetime import datetime

import pandas as pd
from hiveengine.rpc import RPCErrorDoRetry

from src.api import spl, peakmonsters
from src.configuration import store
from src.utils import store_util, land_util, token_util, collection_util, progress_util


def update_portfolio(account, portfolio_df, list_prices_df, market_prices_df):
    do_update = False
    if not portfolio_df.empty:
        date = datetime.today().strftime('%Y-%m-%d')
        if portfolio_df.loc[(portfolio_df.account_name == account) & (portfolio_df.date == date)].empty:
            do_update = True
        else:
            logging.warning("Already pulled portfolio data for this day, no need to run this too often")
    else:
        do_update = True

    if do_update:
        df1 = collection_util.get_card_edition_value(account, list_prices_df, market_prices_df)
        df2 = token_util.get_token_value(account)
        total_df = df1.merge(df2)
        df3 = land_util.get_deeds_value(account)
        total_df = total_df.merge(df3)
        df4 = land_util.get_staked_dec_value(account)
        total_df = total_df.merge(df4)
        portfolio_df = pd.concat([portfolio_df, total_df], ignore_index=True)
    return portfolio_df


def update_portfolios():
    progress_util.update_daily_msg("Start update portfolios")
    list_prices_df = spl.get_all_cards_for_sale_df()
    market_prices_df = peakmonsters.get_market_prices_df()

    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update portfolio for: " + str(account))
        try:
            store.portfolio = update_portfolio(account, store.portfolio.copy(), list_prices_df, market_prices_df)
        except RPCErrorDoRetry:
            progress_util.update_daily_msg("ERROR: Hive market down stop update portfolio", error=True)
            raise RPCErrorDoRetry("Hive market down stop update portfolio")

    store.portfolio.fillna(0, inplace=True)
    store_util.save_stores()
