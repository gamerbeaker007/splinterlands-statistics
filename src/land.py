from datetime import datetime

import pandas as pd

from src.api import spl
from src.configuration import store
from src.utils import store_util, land_util, progress_util

START_LAND_DATE = datetime(2023, 11, 25)


def has_land(account):
    if len(spl.get_deeds_collection(account)) > 0:
        return True
    else:
        return False


def get_last_process_date(account):
    from_date = START_LAND_DATE
    df = store.land.copy()
    if not df.empty and not df.loc[(df.player == account)].empty:
        # determine last process date
        df = df.loc[(df.player == account)]
        df.timestamp = pd.to_datetime(df.timestamp)
        from_date = df.timestamp.max()
    return from_date


def update_land_data():
    progress_util.update_daily_msg("Start update land")

    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update land for: " + str(account))
        if has_land(account):
            from_date = get_last_process_date(account)
            df = land_util.get_land_operations(account, from_date)
            if not df.empty:
                store.land = pd.concat([store.land, df], ignore_index=True)
    store_util.save_stores()

