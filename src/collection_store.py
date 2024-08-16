import pandas as pd

from src.api import spl
from src.configuration import config, store
from src.utils import store_util, progress_util


def update_collection():
    progress_util.update_daily_msg("Start update collections... ")
    current_collection_df = pd.DataFrame()
    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update collection for: " + str(account))
        df = spl.get_player_collection_df(account)
        df.loc[:, 'card_name'] = df.apply(lambda row: config.card_details_df.loc[row['card_detail_id']]['name'], axis=1)

        current_collection_df = pd.concat([current_collection_df, df])

    store.collection = current_collection_df
