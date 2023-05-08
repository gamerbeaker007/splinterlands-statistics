import pandas as pd

from src.api import spl
from src.configuration import config, store


def update_collection():
    current_collection_df = pd.DataFrame()
    for account in config.account_names:
        current_collection_df = pd.concat([current_collection_df, spl.get_player_collection_df(account)])

    if not store.collection_df.empty:
        store.collection_df = current_collection_df.reset_index().merge(store.collection_df.reset_index()['uid'], on='uid', how='left').set_index('uid').sort_index()
        store.collection_df.fillna(0, inplace=True)
    else:
        store.collection_df = current_collection_df
