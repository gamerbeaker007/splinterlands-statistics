import logging
import os

import pandas as pd

from src.api import spl
from src.configuration import store, config


def update_season_end_dates():
    if store.season_end_dates.empty:
        from_season_id = 1
    else:
        from_season_id = store.season_end_dates.id.max() + 1

    till_season_id = spl.get_current_season()['id']
    # logging.info("Update season end dates for '" + str(till_season_id) + "' seasons")
    for season_id in range(from_season_id, till_season_id + 1):
        logging.info("Update season end date for season: '" + str(season_id))

        store.season_end_dates = pd.concat([store.season_end_dates,
                                            spl.get_season_end_time(season_id)],
                                           ignore_index=True)
    save_stores()


def get_store_names():
    stores_arr = []
    for store_name, _store in store.__dict__.items():
        if isinstance(_store, pd.DataFrame):
            stores_arr.append(store_name)
    return stores_arr


def get_store_file(name):
    return os.path.join(config.store_dir, str(config.file_prefix + name + config.file_extension))


# def get_store(name):
#     for store_name, store in stores.__dict__.items():
#         if store_name == name:
#             return store_name, store
#     return None

def load_stores():
    for store_name in get_store_names():
        store_file = get_store_file(store_name)
        if os.path.isfile(store_file):
            store.__dict__[store_name] = pd.read_csv(store_file, index_col=0)


def save_stores():
    for store_name in get_store_names():
        store_file = get_store_file(store_name)
        store.__dict__[store_name].sort_index().to_csv(store_file)


def get_account_names():
    if store.accounts.empty:
        return list()
    else:
        return store.accounts.account_name.tolist()


def get_first_account_name():
    if store.accounts.empty:
        return ""
    else:
        return store.accounts.values[0][0]


def add_account(account_name):
    new_account = pd.DataFrame({'account_name': account_name}, index=[0])
    if store.accounts.empty:
        store.accounts = pd.concat([store.accounts, new_account], ignore_index=True)
    else:
        if store.accounts.loc[(store.accounts.account_name == account_name)].empty:
            store.accounts = pd.concat([store.accounts, new_account], ignore_index=True)
    save_stores()
    return store.accounts.account_name.tolist()


def remove_account_from_store(store_name, search_column, account_name):
    _store = store.__dict__[store_name]
    if search_column in _store.columns.tolist():
        rows = _store.loc[(_store[search_column] == account_name)]
        if not rows.empty:
            _store = _store.drop(rows.index)
    return _store


def remove_data(account_name):
    for store_name in get_store_names():

        store.__dict__[store_name] = remove_account_from_store(store_name, 'account_name', account_name)
        store.__dict__[store_name] = remove_account_from_store(store_name, 'account', account_name)
        store.__dict__[store_name] = remove_account_from_store(store_name, 'player', account_name)

    # account_row = store.accounts.loc[(store.accounts.account_name == account_name)]
    # if not account_row.empty:
    #     store.accounts = store.accounts.drop(account_row.index)
    #
    # rows = store.last_processed.loc[(store.last_processed.account == account_name)]
    # if not rows.empty:
    #     store.last_processed = store.last_processed.drop(rows.index)
    #
    # rows = store.battle.loc[(store.battle.account == account_name)]
    # if not rows.empty:
    #     store.battle = store.battle.drop(rows.index)
    #
    # rows = store.collection.loc[(store.collection.player == account_name)]
    # if not rows.empty:
    #     store.collection = store.collection.drop(rows.index)
    #
    # rows = store.battle_big.loc[(store.battle_big.account == account_name)]
    # if not rows.empty:
    #     store.battle_big = store.battle_big.drop(rows.index)
    #
    # rows = store.rating.loc[(store.rating.account == account_name)]
    # if not rows.empty:
    #     store.rating = store.rating.drop(rows.index)
    #
    # rows = store.losing_big.loc[(store.losing_big.account == account_name)]
    # if not rows.empty:
    #     store.losing_big = store.losing_big.drop(rows.index)
    #
    # store.season_dec.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_dec.loc[(store.season_dec.player == account_name)]
    # if not rows.empty:
    #     store.season_dec = store.season_dec.drop(rows.index)
    #
    # store.season_merits.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_merits.loc[(store.season_merits.player == account_name)]
    # if not rows.empty:
    #     store.season_merits = store.season_merits.drop(rows.index)
    #
    # store.season_unclaimed_sps.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_unclaimed_sps.loc[(store.season_unclaimed_sps.player == account_name)]
    # if not rows.empty:
    #     store.season_unclaimed_sps = store.season_unclaimed_sps.drop(rows.index)
    #
    # store.season_sps.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_sps.loc[(store.season_sps.player == account_name)]
    # if not rows.empty:
    #     store.season_sps = store.season_sps.drop(rows.index)
    #
    # store.season_vouchers.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_vouchers.loc[(store.season_vouchers.player == account_name)]
    # if not rows.empty:
    #     store.season_vouchers = store.season_vouchers.drop(rows.index)
    #
    # store.season_credits.reset_index().drop(columns=['index'], inplace=True)
    # rows = store.season_credits.loc[(store.season_credits.player == account_name)]
    # if not rows.empty:
    #     store.season_credits = store.season_credits.drop(rows.index)

    save_stores()


def remove_account(account_name):
    if store.accounts.empty:
        return list()
    else:
        account_row = store.accounts.loc[(store.accounts.account_name == account_name)]
        if not account_row.empty:
            remove_data(account_name)

    return store.accounts.account_name.tolist()
