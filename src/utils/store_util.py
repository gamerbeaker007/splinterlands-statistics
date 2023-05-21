import logging
import os

import pandas as pd

from src.api import spl
from src.configuration import store


def update_season_end_dates():
    if store.season_end_dates_df.empty:
        from_season_id = 1
    else:
        from_season_id = store.season_end_dates_df.id.max() + 1

    till_season_id = spl.get_current_season()['id']
    logging.info("Update season end dates for '" + str(till_season_id) + "' seasons")
    for season_id in range(from_season_id, till_season_id + 1):
        logging.info("Update season end date for season: '" + str(season_id))

        store.season_end_dates_df = pd.concat([store.season_end_dates_df, spl.get_season_end_time(season_id)])
    save_stores()


def load_stores():
    if os.path.isfile(store.season_end_dates_file):
        store.season_end_dates_df = pd.read_csv(store.season_end_dates_file, index_col=0)

    if os.path.isfile(store.accounts_file):
        store.accounts_df = pd.read_csv(store.accounts_file, index_col=0)

    if os.path.isfile(store.collection_file):
        store.collection_df = pd.read_csv(store.collection_file, index_col=[0]).sort_index()

    if os.path.isfile(store.battle_file):
        store.battle_df = pd.read_csv(store.battle_file, index_col=0)
        store.battle_df = store.battle_df.where(store.battle_df.notnull(), None)

    if os.path.isfile(store.last_processed_file):
        store.last_processed_df = pd.read_csv(store.last_processed_file, index_col=0)

    if os.path.isfile(store.battle_big_file):
        store.battle_big_df = pd.read_csv(store.battle_big_file, index_col=0)

    if os.path.isfile(store.rating_file):
        store.rating_df = pd.read_csv(store.rating_file, index_col=0)

    if os.path.isfile(store.losing_big_file):
        store.losing_big_df = pd.read_csv(store.losing_big_file, index_col=0)

    if os.path.isfile(store.season_dec_file):
        store.season_dec_df = pd.read_csv(store.season_dec_file, index_col=0)

    if os.path.isfile(store.season_merits_file):
        store.season_merits_df = pd.read_csv(store.season_merits_file, index_col=0)

    if os.path.isfile(store.season_unclaimed_sps_file):
        store.season_unclaimed_sps_df = pd.read_csv(store.season_unclaimed_sps_file, index_col=0)

    if os.path.isfile(store.season_sps_file):
        store.season_sps_df = pd.read_csv(store.season_sps_file, index_col=0)

    if os.path.isfile(store.season_vouchers_file):
        store.season_vouchers_df = pd.read_csv(store.season_vouchers_file, index_col=0)

    if os.path.isfile(store.season_credits_file):
        store.season_credits_df = pd.read_csv(store.season_credits_file, index_col=0)


def save_stores():
    store.season_end_dates_df.sort_index().to_csv(store.season_end_dates_file)
    store.accounts_df.sort_index().to_csv(store.accounts_file)
    store.last_processed_df.sort_index().to_csv(store.last_processed_file)
    store.battle_df.sort_index().to_csv(store.battle_file)
    store.collection_df.sort_index().to_csv(store.collection_file)
    store.battle_big_df.sort_index().to_csv(store.battle_big_file)
    store.rating_df.sort_index().to_csv(store.rating_file)
    store.losing_big_df.sort_index().to_csv(store.losing_big_file)
    store.season_dec_df.sort_index().to_csv(store.season_dec_file)
    store.season_merits_df.sort_index().to_csv(store.season_merits_file)
    store.season_unclaimed_sps_df.sort_index().to_csv(store.season_unclaimed_sps_file)
    store.season_sps_df.sort_index().to_csv(store.season_sps_file)
    store.season_vouchers_df.sort_index().to_csv(store.season_vouchers_file)
    store.season_credits_df.sort_index().to_csv(store.season_credits_file)


def get_account_names():
    if store.accounts_df.empty:
        return list()
    else:
        return store.accounts_df.account_name.tolist()


def get_first_account_name():
    if store.accounts_df.empty:
        return ""
    else:
        return store.accounts_df.loc[0].account_name


def add_account(account_name):
    new_account = pd.DataFrame({'account_name': account_name}, index=[0])
    if store.accounts_df.empty:
        store.accounts_df = pd.concat([store.accounts_df, new_account], ignore_index=True)
    else:
        if store.accounts_df.loc[(store.accounts_df.account_name == account_name)].empty:
            store.accounts_df = pd.concat([store.accounts_df, new_account], ignore_index=True)
    save_stores()
    return store.accounts_df.account_name.tolist()



def remove_data(account_name):
    account_row = store.accounts_df.loc[(store.accounts_df.account_name == account_name)]
    if not account_row.empty:
        store.accounts_df = store.accounts_df.drop(account_row.index)

    rows = store.last_processed_df.loc[(store.last_processed_df.account == account_name)]
    if not rows.empty:
        store.last_processed_df = store.last_processed_df.drop(rows.index)

    rows = store.battle_df.loc[(store.battle_df.account == account_name)]
    if not rows.empty:
        store.battle_df = store.battle_df.drop(rows.index)

    rows = store.collection_df.loc[(store.collection_df.player == account_name)]
    if not rows.empty:
        store.collection_df = store.collection_df.drop(rows.index)

    rows = store.battle_big_df.loc[(store.battle_big_df.account == account_name)]
    if not rows.empty:
        store.battle_big_df = store.battle_big_df.drop(rows.index)

    rows = store.rating_df.loc[(store.rating_df.account == account_name)]
    if not rows.empty:
        store.rating_df = store.rating_df.drop(rows.index)

    rows = store.losing_big_df.loc[(store.losing_big_df.account == account_name)]
    if not rows.empty:
        store.losing_big_df = store.losing_big_df.drop(rows.index)

    store.season_dec_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_dec_df.loc[(store.season_dec_df.player == account_name)]
    if not rows.empty:
        store.season_dec_df = store.season_dec_df.drop(rows.index)

    store.season_merits_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_merits_df.loc[(store.season_merits_df.player == account_name)]
    if not rows.empty:
        store.season_merits_df = store.season_merits_df.drop(rows.index)

    store.season_unclaimed_sps_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_unclaimed_sps_df.loc[(store.season_unclaimed_sps_df.player == account_name)]
    if not rows.empty:
        store.season_unclaimed_sps_df = store.season_unclaimed_sps_df.drop(rows.index)

    store.season_sps_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_sps_df.loc[(store.season_sps_df.player == account_name)]
    if not rows.empty:
        store.season_sps_df = store.season_sps_df.drop(rows.index)

    store.season_vouchers_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_vouchers_df.loc[(store.season_vouchers_df.player == account_name)]
    if not rows.empty:
        store.season_vouchers_df = store.season_vouchers_df.drop(rows.index)

    store.season_credits_df.reset_index().drop(columns=['index'], inplace=True)
    rows = store.season_credits_df.loc[(store.season_credits_df.player == account_name)]
    if not rows.empty:
        store.season_credits_df = store.season_credits_df.drop(rows.index)

    save_stores()


def remove_account(account_name):
    if store.accounts_df.empty:
        return list()
    else:
        account_row = store.accounts_df.loc[(store.accounts_df.account_name == account_name)]
        if not account_row.empty:
            remove_data(account_name)

    return store.accounts_df.account_name.tolist()
