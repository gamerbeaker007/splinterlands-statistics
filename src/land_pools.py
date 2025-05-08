import logging
from datetime import datetime

import pandas as pd

from src.configuration import store
from src.utils import store_util, land_util, progress_util


def update_land_pools_for_account(account, land_pools):
    do_update = False
    if not land_pools.empty:
        date = datetime.today().strftime('%Y-%m-%d')
        if land_pools.loc[(land_pools.account_name == account) & (land_pools.date == date)].empty:
            do_update = True
        else:
            logging.warning("Already pulled land pool data for this day, no need to run this too often")
    else:
        do_update = True

    if do_update:
        df1 = land_util.get_liquidity_pools_info(account)
        land_pools = pd.concat([land_pools, df1], ignore_index=True)
    return land_pools


def update_pools():
    progress_util.update_daily_msg("Start update land")

    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update land pools for: " + str(account))
        store.land_pools = update_land_pools_for_account(account, store.land_pools.copy())

    store_util.save_stores()
