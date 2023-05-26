import pandas as pd

from src.api import spl
from src.configuration import config, store
from src.utils import store_util


def update_collection():
    current_collection_df = pd.DataFrame()
    for account in store_util.get_account_names():
        df = spl.get_player_collection_df(account)
        df['card_name'] = df.apply(lambda row: config.card_details_df.loc[row['card_detail_id']]['name'], axis=1)
        current_collection_df = pd.concat([current_collection_df, df])

    if not store.collection.empty:
        store.collection = current_collection_df.reset_index().merge(store.collection.reset_index()['uid'], on='uid', how='left').set_index('uid').sort_index()
        store.collection.fillna(0, inplace=True)
    else:
        store.collection = current_collection_df
