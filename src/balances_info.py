import logging

import numpy as np
import pandas as pd
from dateutil import parser

from src.api import spl
from src.configuration import store, config
from src.utils import store_util


def get_balances_account(account_name):
    current_season_data = config.current_season

    if not (store.season_sps_df.empty or store.season_sps_df.loc[store.season_sps_df.player == account_name].empty):
        pass
    else:
        dec_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="DEC"))
        unclaimed_sps_df = pd.DataFrame(
            spl.get_balance_history_for_token(account_name, token="SPS", unclaimed_sps=True))
        sps_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="SPS"))
        merits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="MERITS"))
        credits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="CREDITS"))
        vouchers_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="VOUCHER"))

        first_season = determine_first_season_id_played(dec_df)
        season_array = np.arange(first_season, current_season_data['id'])
        store.season_dec_df = process_season_balances(dec_df, store.season_dec_df.copy(), account_name, season_array)
        store.season_unclaimed_sps_df = process_season_balances(unclaimed_sps_df, store.season_unclaimed_sps_df.copy(),
                                                                account_name, season_array)
        store.season_sps_df = process_season_balances(sps_df, store.season_sps_df.copy(), account_name, season_array)
        store.season_merits_df = process_season_balances(merits_df, store.season_merits_df.copy(), account_name,
                                                         season_array)
        store.season_vouchers_df = process_season_balances(vouchers_df, store.season_vouchers_df.copy(), account_name,
                                                           season_array)
        store.season_credits_df = process_season_balances(credits_df, store.season_credits_df.copy(), account_name,
                                                          season_array)

        # get all info
        store_util.save_stores()


def process_season_balances(balance_df, store_copy, account_name, season_array):
    season_end_times = config.season_end_dates_array
    for season_id in season_array:
        end_date = [season_end_time['date'] for season_end_time in season_end_times if
                    season_end_time["id"] == season_id][0]
        start_date = [season_end_time['date'] for season_end_time in season_end_times if
                      season_end_time["id"] == season_id - 1][0]

        balance_df.created_date = pd.to_datetime(balance_df.created_date)
        balance_df.amount = pd.to_numeric(balance_df.amount)

        for search_type in balance_df['type'].unique().tolist():
            logging.info("Processing (" + str(account_name) + ") search_type" + str(search_type))
            # when season rewards are found these always belong to a previous season (timeframe)
            if search_type == 'season_rewards':
                end_date = [season_end_time['date'] for season_end_time in season_end_times if
                            season_end_time["id"] == season_id + 1][0]
                start_date = [season_end_time['date'] for season_end_time in season_end_times if
                              season_end_time["id"] == season_id][0]

            balance_mask = (balance_df['created_date'] > start_date) & (balance_df['created_date'] <= end_date) & (
                    balance_df['type'] == search_type)
            if 'season' not in store_copy.columns.tolist() or \
                    store_copy.loc[(store_copy.season == season_id) & (store_copy.player == account_name)].empty:
                store_copy = pd.concat([store_copy,
                                        pd.DataFrame({'season': season_id,
                                                      'player': account_name}, index=[0])])

            store_copy.loc[(store_copy.season == season_id) & (store_copy.player == account_name), search_type] = balance_df.loc[balance_mask].amount.sum()
    return store_copy


def determine_first_season_id_played(balance_history_dec_df):
    first_earned_date_str = balance_history_dec_df.created_date.sort_values().values[0]
    first_earned_date = parser.parse(first_earned_date_str)

    season_end_times = config.season_end_dates_array
    # determine which was the first season earning start
    for season_end_time in season_end_times:
        if first_earned_date <= season_end_time['date']:
            return season_end_time['id']


def get_balances():
    for account in config.account_names:
        get_balances_account(account)
