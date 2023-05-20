import os

import pandas as pd

from src.configuration import store


def load_stores():
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
