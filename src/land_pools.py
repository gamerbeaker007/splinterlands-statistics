import logging
from datetime import datetime

import pandas as pd

from src.configuration import store, config
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


def update_land_resource(land_resources):
    do_update = False
    if not land_resources.empty:
        date = datetime.today().strftime('%Y-%m-%d')
        if land_resources.loc[land_resources.date == date].empty:
            do_update = True
        else:
            logging.warning("Already pulled land resource data for this day, no need to run this too often")
    else:
        do_update = True

    if do_update:
        df1 = land_util.get_land_resources_info()
        land_resources = pd.concat([land_resources, df1], ignore_index=True)
    return land_resources


def update_land_region(land_region):
    do_update = False
    if not land_region.empty:
        date = datetime.today().strftime('%Y-%m-%d')
        if land_region.loc[land_region.date == date].empty:
            do_update = True
        else:
            logging.warning("Already pulled land region data for this day, no need to run this too often")
    else:
        do_update = True

    if do_update:
        df1 = land_util.get_land_region_info()
        land_region = pd.concat([land_region, df1], ignore_index=True)
    return land_region


def update_pools():
    progress_util.update_daily_msg("Start update land")

    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...update land pools for: " + str(account))
        store.land_pools = update_land_pools_for_account(account, store.land_pools.copy())

    store.land_resources = update_land_resource(store.land_resources.copy())
    store_util.save_stores()

    if config.server_mode:
        store.land_region = update_land_region(store.land_region.copy())
        store.land.fillna(0, inplace=True)
    else:
        logging.warning('Skip land region update not running in server mode...')

    store_util.save_stores()
