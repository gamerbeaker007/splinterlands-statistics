import numpy as np
import pandas as pd

from src.api import spl
from src.utils import progress_util


def get_season_battles(account_name, store_df, mode, current_season_data):
    if not (store_df.empty or
            store_df.loc[store_df.player == account_name].empty):
        next_season = store_df.loc[
                          store_df.player == account_name].season.max() + 1
        season_array = np.arange(next_season, current_season_data['id'])

    else:
        season_array = np.arange(1, current_season_data['id'])

    if len(season_array) > 0:
        for season_id in season_array:
            progress_util.update_season_msg("Gathering (" + str(account_name) + ", "
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
        progress_util.update_season_msg("No new season battle info found for: " + str(account_name))

    progress_util.update_season_msg("Gathering '" + str(account_name) + ", "
                                    + str(mode.value) +
                                    "' battle info done..")

    return store_df
