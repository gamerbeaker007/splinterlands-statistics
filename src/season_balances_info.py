import numpy as np
import pandas as pd
from dateutil import parser

from src.configuration import store
from src.utils import store_util, progress_util, spl_util


def update_balances_store(account_name, current_season_data):
    if not (store.season_sps.empty or store.season_sps.loc[store.season_sps.player == account_name].empty):
        start_from_season = store.season_sps.loc[store.season_sps.player == account_name].season_id.max() + 1

        if start_from_season == current_season_data['id']:
            progress_util.update_season_msg("No new season balances to process for: " + str(account_name))
            return

        season_array = np.arange(start_from_season, current_season_data['id'])
        start_date, end_date = get_start_end_time_season(start_from_season)
        start_date = parser.parse(start_date)
        dec_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="DEC",
            )
        )
        unclaimed_sps_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="SPS",
                unclaimed_sps=True,
            )
        )
        sps_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="SPS",
            )
        )
        merits_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="MERITS",
            )
        )
        credits_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="CREDITS",
            )
        )
        vouchers_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                from_date=start_date,
                token="VOUCHER",
            )
        )

    else:
        dec_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="DEC",
            )
        )

        unclaimed_sps_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="SPS",
                unclaimed_sps=True,
            )
        )
        sps_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="SPS",
            )
        )
        merits_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="MERITS",
            )
        )
        credits_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="CREDITS",
            )
        )
        vouchers_df = pd.DataFrame(
            spl_util.get_balance_history_for_token(
                account_name,
                token="VOUCHER",
            )
        )

        # Concatenate the dataframes
        combined_df = pd.concat([dec_df, unclaimed_sps_df, sps_df, merits_df, credits_df, vouchers_df],
                                ignore_index=True)

        first_season = determine_first_season_id_played(combined_df)
        season_array = np.arange(first_season, current_season_data['id'])

    if len(season_array) > 0:
        progress_util.update_season_msg("Start processing DEC")
        store.season_dec = process_season_balances(dec_df, store.season_dec.copy(), account_name, season_array)
        progress_util.update_season_msg("Start processing UNCLAIMED SPS")
        store.season_unclaimed_sps = process_season_balances(unclaimed_sps_df, store.season_unclaimed_sps.copy(),
                                                             account_name, season_array, unclaimed_sps=True)
        progress_util.update_season_msg("Start processing SPS")
        store.season_sps = process_season_balances(sps_df, store.season_sps.copy(), account_name, season_array)
        progress_util.update_season_msg("Start processing MERITS")
        store.season_merits = process_season_balances(merits_df, store.season_merits.copy(), account_name,
                                                      season_array)
        progress_util.update_season_msg("Start processing VOUCHERS")
        store.season_vouchers = process_season_balances(vouchers_df, store.season_vouchers.copy(), account_name,
                                                        season_array)
        progress_util.update_season_msg("Start processing CREDITS")
        store.season_credits = process_season_balances(credits_df, store.season_credits.copy(), account_name,
                                                       season_array)
    progress_util.update_season_msg("Get balances for account (" + str(account_name) + ") Done")
    store_util.save_stores()


def process_season_rewards(balance_df, store_copy, account_name, season_id, search_type,
                           unclaimed_sps=False, unclaimed_sps_rewards_share=False):
    # when season rewards are found these always belong to a previous season
    # timeframe of the claim rewards is always in the new season

    # if the balance of the current season is greater than 0 update the previous season
    column_name = search_type
    if unclaimed_sps_rewards_share:
        column_name = search_type + "_fee"
    start_date, end_date = get_start_end_time_season(season_id)
    balance_mask = get_balance_mask(account_name,
                                    balance_df,
                                    start_date,
                                    end_date,
                                    search_type,
                                    unclaimed_sps,
                                    unclaimed_sps_rewards_share)
    amount = balance_df.loc[balance_mask].amount.sum()
    if amount > 0:
        store_copy.loc[(store_copy.season_id == season_id - 1)
                       & (store_copy.player == account_name), column_name] = amount

    # if for the new season already a claim is done also capture this season rewards to the current
    start_date, end_date = get_start_end_time_season(season_id + 1)
    balance_mask = get_balance_mask(account_name,
                                    balance_df,
                                    start_date,
                                    end_date,
                                    search_type,
                                    unclaimed_sps,
                                    unclaimed_sps_rewards_share)
    store_copy.loc[(store_copy.season_id == season_id)
                   & (store_copy.player == account_name), column_name] = balance_df.loc[balance_mask].amount.sum()

    return store_copy


def get_balance_mask(account_name, balance_df, start_date, end_date, search_type,
                     unclaimed_sps=False, unclaimed_sps_reward_share=False):
    if unclaimed_sps_reward_share:
        return (balance_df.created_date > start_date) \
            & (balance_df.created_date <= end_date) \
            & (balance_df.type == search_type) \
            & (balance_df.amount < 0.0) \
            & (balance_df.to_player != account_name) \
            & (balance_df.to_player.notnull())
    elif unclaimed_sps:
        return (balance_df.created_date > start_date) \
            & (balance_df.created_date <= end_date) \
            & (balance_df.type == search_type) \
            & (balance_df.amount > 0.0)
    else:
        return (balance_df.created_date > start_date) & \
            (balance_df.created_date <= end_date) & \
            (balance_df.type == search_type)


def process_season_balances(balance_df, store_copy, account_name, season_array, unclaimed_sps=False):
    if not balance_df.empty:
        for season_id in season_array:
            store_copy = add_season_id(account_name, season_id, store_copy)

            start_date, end_date = get_start_end_time_season(season_id)

            balance_df.created_date = pd.to_datetime(balance_df.created_date)
            balance_df.amount = pd.to_numeric(balance_df.amount)

            for search_type in balance_df['type'].unique().tolist():
                progress_util.update_season_msg("Processing season '" + str(season_id) +
                                                "' for '" + str(account_name) +
                                                "' type: " + str(search_type))

                # special treatment for season_rewards they are in different timeframe
                # for unclaimed sps season_rewards are season called
                if search_type == 'season_rewards' or (unclaimed_sps and search_type == 'season'):
                    store_copy = process_season_rewards(balance_df, store_copy, account_name, season_id, search_type,
                                                        unclaimed_sps)
                    # For unclaimed SPS season process it twice one for the rewards and one for shared reward/fees
                    if search_type == 'season':
                        store_copy = process_season_rewards(balance_df, store_copy, account_name, season_id,
                                                            search_type,
                                                            unclaimed_sps, True)
                else:
                    balance_mask = get_balance_mask(account_name,
                                                    balance_df,
                                                    start_date,
                                                    end_date,
                                                    search_type,
                                                    unclaimed_sps)

                    if search_type == 'market_purchase':
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name),
                                       'sell_' + search_type] = balance_df.loc[
                            balance_mask & (pd.to_numeric(balance_df.amount) > 0)].amount.sum()
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name),
                                       'buy_' + search_type] = balance_df.loc[
                            balance_mask & (pd.to_numeric(balance_df.amount) < 0)].amount.sum()
                    elif search_type == 'rental_payment':
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name),
                                       'earn_' + search_type] = balance_df.loc[
                            balance_mask & (pd.to_numeric(balance_df.amount) > 0)].amount.sum()
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name),
                                       'cost_' + search_type] = balance_df.loc[
                            balance_mask & (pd.to_numeric(balance_df.amount) < 0)].amount.sum()

                    else:
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name), search_type] = balance_df.loc[
                            balance_mask].amount.sum()

                    # For unclaimed SPS process it twice one for the rewards and one for shared reward/fees
                    if unclaimed_sps:
                        balance_mask = get_balance_mask(account_name,
                                                        balance_df,
                                                        start_date,
                                                        end_date,
                                                        search_type,
                                                        unclaimed_sps, True)
                        store_copy.loc[(store_copy.season_id == season_id)
                                       & (store_copy.player == account_name), search_type + "_fee"] = balance_df.loc[
                            balance_mask].amount.sum()

    return store_copy


def add_season_id(account_name, season_id, store_copy):
    # if season id is not in the table yet first add it
    if 'season' not in store_copy.columns.tolist() or \
            store_copy.loc[(store_copy.season == season_id) & (store_copy.player == account_name)].empty:
        store_copy = pd.concat([store_copy,
                                pd.DataFrame({'season_id': season_id,
                                              'player': account_name}, index=[0])], ignore_index=True)
    return store_copy


def determine_first_season_id_played(df):
    first_earned_date_str = df.created_date.sort_values().dropna().values[0]
    first_earned_date = parser.parse(first_earned_date_str)

    season_end_times = store.season_end_dates
    # determine which was the first season earning start
    for index, season_end_time in season_end_times.iterrows():
        # for season_end_time in season_end_times:
        if first_earned_date <= parser.parse(season_end_time['end_date']):
            return season_end_time['id']


def get_start_end_time_season(season_id):
    return store.season_end_dates.loc[(store.season_end_dates.id == season_id - 1)]['end_date'].values[0], \
        store.season_end_dates.loc[(store.season_end_dates.id == season_id)]['end_date'].values[0]
