import asyncio

from src.utils import store_util

SERVER_MODE_INTERVAL_IN_MINUTES = 90


async def async_update_task():
    """ async function"""
    while True:
        store_util.update_data(battle_update=True, season_update=True)
        await asyncio.sleep(SERVER_MODE_INTERVAL_IN_MINUTES*60)


async def async_background_task():
    """Main async function"""
    await asyncio.gather(async_update_task())


def async_background_task_wrapper():
    """Not async Wrapper around async_main to run it as target function of Thread"""
    asyncio.run(async_background_task())
