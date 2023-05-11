import json
import logging
import os

from src import battle_store, collection_store, analyse
from src.api import spl
import pandas as pd

from src.configuration import config, store
from src.static.static_values_enum import MatchType


def load_stores():
    if os.path.isfile(store.collection_file):
        store.collection_df = pd.read_csv(store.collection_file, index_col=[0]).sort_index()

    if os.path.isfile(store.battle_file):
        store.battle_df = pd.read_csv(store.battle_file, index_col=0)
        store.battle_df = store.battle_df.where(store.battle_df.notnull(), None)
    # else:
    #     store.battle_df = pd.DataFrame(columns=['uid', 'match_type', 'format', 'win', 'loss'])

    if os.path.isfile(store.last_processed_file):
        store.last_processed_df = pd.read_csv(store.last_processed_file, index_col=0)
    # else:
    #     store.last_processed_df = pd.DataFrame(columns=['account', 'last_processed'])

    if os.path.isfile(store.battle_big_file):
        store.battle_big_df = pd.read_csv(store.battle_big_file, index_col=0)

    if os.path.isfile(store.rating_file):
        store.rating_df = pd.read_csv(store.rating_file, index_col=0)

    if os.path.isfile(store.losing_big_file):
        store.losing_big_df = pd.read_csv(store.losing_big_file, index_col=0)


def save_stores():
    store.last_processed_df.sort_index().to_csv(store.last_processed_file)
    store.battle_df.sort_index().to_csv(store.battle_file)
    store.collection_df.sort_index().to_csv(store.collection_file)
    store.battle_big_df.sort_index().to_csv(store.battle_big_file)
    store.rating_df.sort_index().to_csv(store.rating_file)
    store.losing_big_df.sort_index().to_csv(store.losing_big_file)

def main():
    load_stores()

    collection_store.update_collection()
    battle_store.process_battles()

    analyse.print_top_ten_losing(MatchType.CHALLENGE)
    analyse.print_top_ten_losing(MatchType.TOURNAMENT)
    analyse.print_top_ten_losing(MatchType.RANKED)
    analyse.print_top_ten_losing()

    save_stores()

    print(config.account_names)


if __name__ == '__main__':
    main()
