import logging

import numpy as np
import pandas as pd
from dateutil import parser

from src.api import spl
from src.configuration import store, config
from src.utils import store_util


def update_balances_store(account_name):
    current_season_data = config.current_season

    if not (store.season_sps_df.empty or store.season_sps_df.loc[store.season_sps_df.player == account_name].empty):
        start_from_season = store.season_sps_df.loc[store.season_sps_df.player == account_name].season_id.max() + 1

        if start_from_season == current_season_data['id']:
            logging.info("No new season balances to process for: " + str(account_name))
            return

        season_array = np.arange(start_from_season, current_season_data['id'])
        start_date, end_date = get_start_end_time_season(start_from_season)
        start_date = parser.parse(start_date)
        dec_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                from_date=start_date,
                                                                token="DEC"))
        unclaimed_sps_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                          from_date=start_date,
                                                                          token="SPS",
                                                                          unclaimed_sps=True))
        sps_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                from_date=start_date,
                                                                token="SPS"))
        merits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                   from_date=start_date,
                                                                   token="MERITS"))
        credits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                    from_date=start_date,
                                                                    token="CREDITS"))
        vouchers_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                     from_date=start_date,
                                                                     token="VOUCHER"))

    else:
        dec_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,token="DEC"))
        unclaimed_sps_df = pd.DataFrame(spl.get_balance_history_for_token(account_name,
                                                                          token="SPS",
                                                                          unclaimed_sps=True))
        sps_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="SPS"))
        merits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="MERITS"))
        credits_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="CREDITS"))
        vouchers_df = pd.DataFrame(spl.get_balance_history_for_token(account_name, token="VOUCHER"))

        first_season = determine_first_season_id_played(dec_df)
        season_array = np.arange(first_season, current_season_data['id'])

    if len(season_array) > 0:
        logging.info("Start processing DEC")
        store.season_dec_df = process_season_balances(dec_df, store.season_dec_df.copy(), account_name, season_array)
        logging.info("Start processing UNCLAIMED SPS")
        store.season_unclaimed_sps_df = process_season_balances(unclaimed_sps_df, store.season_unclaimed_sps_df.copy(),
                                                                account_name, season_array, unclaimed_sps=True)
        logging.info("Start processing SPS")
        store.season_sps_df = process_season_balances(sps_df, store.season_sps_df.copy(), account_name, season_array)
        logging.info("Start processing MERITS")
        store.season_merits_df = process_season_balances(merits_df, store.season_merits_df.copy(), account_name,
                                                         season_array)
        logging.info("Start processing VOUCHERS")
        store.season_vouchers_df = process_season_balances(vouchers_df, store.season_vouchers_df.copy(), account_name,
                                                           season_array)
        logging.info("Start processing CREDITS")
        store.season_credits_df = process_season_balances(credits_df, store.season_credits_df.copy(), account_name,
                                                          season_array)
    logging.info("Get balances for account (" + str(account_name) + ") Done")
    store_util.save_stores()


def process_season_rewards(balance_df, store_copy, account_name, season_id, search_type, positive_only):
    # when season rewards are found these always belong to a previous season
    # timeframe of the claim rewards is always in the new season

    # if the balance of the current season is greater than 0 update the previous season
    start_date, end_date = get_start_end_time_season(season_id)
    balance_mask = get_balance_mask(balance_df, end_date, search_type, start_date, positive_only)
    amount = balance_df.loc[balance_mask].amount.sum()
    if amount > 0:
        store_copy.loc[(store_copy.season_id == season_id-1) & (store_copy.player == account_name), search_type] = amount

    # if for the new season already a claim is done also capture this season rewards to the current
    start_date, end_date = get_start_end_time_season(season_id + 1)
    balance_mask = get_balance_mask(balance_df, end_date, search_type, start_date, positive_only)
    amount = balance_df.loc[balance_mask].amount.sum()
    store_copy.loc[(store_copy.season_id == season_id) & (store_copy.player == account_name), search_type] = amount

    return store_copy


def get_balance_mask(balance_df, end_date, search_type, start_date, positive_only):
    if positive_only:
        return (balance_df['created_date'] > start_date) & \
            (balance_df['created_date'] <= end_date) & \
            (balance_df['type'] == search_type) & \
            (balance_df['amount'] > 0.0)
    else:
        return (balance_df['created_date'] > start_date) & \
            (balance_df['created_date'] <= end_date) & \
            (balance_df['type'] == search_type)


def process_season_balances(balance_df, store_copy, account_name, season_array, unclaimed_sps=False):
    positive_only = False
    if unclaimed_sps:
        positive_only = True

    if not balance_df.empty:
        for season_id in season_array:
            store_copy = add_season_id(account_name, season_id, store_copy)

            start_date, end_date = get_start_end_time_season(season_id)

            balance_df.created_date = pd.to_datetime(balance_df.created_date)
            balance_df.amount = pd.to_numeric(balance_df.amount)

            for search_type in balance_df['type'].unique().tolist():
                logging.info("Processing season '" + str(season_id) + "' for '" + str(account_name) + "' type: " + str(search_type))

                # special treatment for season_rewards they are in different timeframe
                # for unclaimed sps season_rewards are season called
                if search_type == 'season_rewards' or (positive_only and search_type == 'season'):
                    store_copy = process_season_rewards(balance_df, store_copy, account_name, season_id, search_type,
                                                        positive_only)
                else:
                    balance_mask = get_balance_mask(balance_df, end_date, search_type, start_date, positive_only)

                    store_copy.loc[(store_copy.season_id == season_id) & (store_copy.player == account_name), search_type] = \
                        balance_df.loc[balance_mask].amount.sum()
    return store_copy


def add_season_id(account_name, season_id, store_copy):
    # if season id is not in the table yet first add it
    if 'season' not in store_copy.columns.tolist() or \
            store_copy.loc[(store_copy.season == season_id) & (store_copy.player == account_name)].empty:
        store_copy = pd.concat([store_copy,
                                pd.DataFrame({'season_id': season_id,
                                              'player': account_name}, index=[0])], ignore_index=True)
    return store_copy


def determine_first_season_id_played(balance_history_dec_df):
    first_earned_date_str = balance_history_dec_df.created_date.sort_values().values[0]
    first_earned_date = parser.parse(first_earned_date_str)

    season_end_times = store.season_end_dates_df
    # determine which was the first season earning start
    for index, season_end_time in season_end_times.iterrows():
        # for season_end_time in season_end_times:
        if first_earned_date <= parser.parse(season_end_time['end_date']):
            return season_end_time['id']


def get_start_end_time_season(season_id):
    return store.season_end_dates_df.loc[(store.season_end_dates_df.id == season_id - 1)]['end_date'].values[0],\
        store.season_end_dates_df.loc[(store.season_end_dates_df.id == season_id)]['end_date'].values[0]


def update_season_balances_store():
    for account in store_util.get_account_names():
        update_balances_store(account)
