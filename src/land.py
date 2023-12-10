import logging
from datetime import datetime

import pandas as pd

from src.api import spl
from src.configuration import store
from src.utils import store_util, land_util, progress_util

START_LAND_DATE = "2023-11-25 00:00:00"


def post_process_land_data(land_df):
    # Add grain column after taxes

    # TODO define what todo more
    return land_df


def update_land(account, land_df):
    if len(spl.get_deeds_collection(account)) > 0:
        from_date = datetime.strptime(START_LAND_DATE, '%Y-%m-%d %H:%M:%S')
        if not land_df.empty and not land_df.loc[(store.land.account_name == account)].emtpy:
            # determine last process date
            land_df = land_df.loc[(store.land.account_name == account)]
            land_df.created_date = pd.to_datetime(land_df.created_date)
            from_date = land_df.created_date.max()
            from_date = datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S')

        # Always till current date
        till_date = datetime.now()
        land_df = land_util.get_land_operations(account, from_date, till_date)

        land_df = post_process_land_data(land_df)
    return land_df


def update_land_data():
    progress_util.update_daily_msg("Start update land")

    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update land for: " + str(account))
        df = update_land(account, store.land.copy())
        store.land = pd.concat([store.land, df], ignore_index=True)
    store_util.save_stores()

