import json
import logging
import os

from src import battle_store, collection_store
from src.api import spl
import pandas as pd

from src.configuration import config, store


def load_stores():
    if os.path.isfile(store.collection_file):
        store.collection_df = pd.read_csv(store.collection_file, index_col=[0]).sort_index()

    if os.path.isfile(store.battle_file):
        store.battle_df = pd.read_csv(store.battle_file, index_col=0)
        store.battle_df = store.battle_df.where(store.battle_df.notnull(), None)
    else:
        store.battle_df = pd.DataFrame(columns=['uid', 'match_type', 'format', 'win', 'loss'])

    if os.path.isfile(store.last_processed_file):
        store.last_processed_df = pd.read_csv(store.last_processed_file, index_col=0)
    else:
        store.last_processed_df = pd.DataFrame(columns=['account', 'last_processed'])

    if os.path.isfile(store.battle_big_file):
        store.battle_big_df = pd.read_csv(store.battle_big_file, index_col=0)


def save_stores():
    # save battle store
    store.last_processed_df.sort_index().to_csv(store.last_processed_file)

    # save battle store
    store.battle_df.sort_index().to_csv(store.battle_file)

    # save collection store
    store.collection_df.sort_index().to_csv(store.collection_file)

    # save battle big store
    store.battle_big_df.sort_index().to_csv(store.battle_big_file)


def main():
    load_stores()

    collection_store.update_collection()
    battle_store.process_battles()

    save_stores()

    print(config.account_names)


if __name__ == '__main__':
    main()
