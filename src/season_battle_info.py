import logging

import numpy as np
import pandas as pd

from src.api import spl
from src.configuration import store, config
from src.static.static_values_enum import Format
from src.utils import store_util


def get_season_battles(account_name, store_df, mode):
    current_season_data = config.current_season

    if not (store_df.empty or
            store_df.loc[store_df.player == account_name].empty):
        next_season = store_df.loc[
                          store_df.player == account_name].season.max() + 1
        season_array = np.arange(next_season, current_season_data['id'])

    else:
        season_array = np.arange(1, current_season_data['id'])

    if len(season_array) > 0:
        for season_id in season_array:
            logging.info("Gathering (" + str(account_name) + ", "
                         + str(mode.value) +
                         ") battle info for season :" + str(season_id))
            result = spl.get_leaderboard_with_player_season(account_name, season_id, mode)
            if 'rank' in result:
                store_df = pd.concat([store_df,
                                      pd.DataFrame(result, index=[0])],
                                     ignore_index=True)
            else:
                store_df = pd.concat([store_df,
                                      pd.DataFrame({'player': account_name, 'season': season_id}, index=[0])],
                                     ignore_index=True)
    else:
        logging.info("No new season battle info found for: " + str(account_name))

    logging.info("Gathering '" + str(account_name) + ", "
                 + str(mode.value) +
                 ") battle info done..")

    return store_df


def update_season_battle_store():
    for account in store_util.get_account_names():
        store.season_modern_battle_info = get_season_battles(account, store.season_modern_battle_info.copy(), Format.MODERN)
        store.season_wild_battle_info = get_season_battles(account, store.season_wild_battle_info.copy(), Format.WILD)
    store_util.save_stores()
