import json
import logging
import time
from threading import Thread

from dash import ctx

from src.api import spl
from src.configuration import store, config
from src.pages.main_dash import app
from src.pages.navigation_pages import navigation_page
from src.static.static_values_enum import Format, MatchType
from src.utils import store_util, update

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    pass


def measure_duration(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        # Log the duration
        logging.info(f"Function '{func.__name__}' took {duration:.4f} seconds to execute. tigger: '{ctx.triggered_id}'")

        return result

    return wrapper


def main():
    migrate_data()

    if config.server_mode:
        th = Thread(target=update.async_background_task_wrapper)
        th.start()

    app.layout = navigation_page.layout
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', debug=config.debug)


if __name__ == '__main__':
    main()
