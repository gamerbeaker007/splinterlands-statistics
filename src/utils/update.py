import asyncio

from src import collection_store, battle_store, portfolio
from src.utils import progress_util, store_util

SERVER_MODE_INTERVAL_IN_MINUTES = 1


def update_data():
    progress_util.set_daily_title('Update collection')
    collection_store.update_collection()

    progress_util.set_daily_title('Update battles')
    battle_store.process_battles()

    progress_util.set_daily_title('Update portfolio')
    portfolio.update_portfolios()

    store_util.save_stores()
    progress_util.update_daily_msg('Done')


async def async_update_task():
    """ async function"""
    while True:
        update_data()
        await asyncio.sleep(SERVER_MODE_INTERVAL_IN_MINUTES*60)


async def async_main():
    """Main async function"""
    await asyncio.gather(async_update_task())


def async_main_wrapper():
    """Not async Wrapper around async_main to run it as target function of Thread"""
    asyncio.run(async_main())
