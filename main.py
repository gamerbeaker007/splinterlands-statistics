import logging
from threading import Thread

from src.configuration import config, store
from src.pages.main_dash import app
from src.pages.navigation_pages import navigation_page
from src.utils import store_util, update

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    # Check if there are any columns that start with 'rebellion_soulbound'
    if any(col.startswith('rebellion_soulbound') for col in store.portfolio.columns):
        logging.info("Migrating rebellion_soulbound -> soulboundrb")
        # Rename columns that start with 'rebellion_soulbound' to 'soulboundrb'
        store.portfolio.rename(
            columns=lambda col: col.replace('rebellion_soulbound', 'soulboundrb') if col.startswith(
                'rebellion_soulbound') else col, inplace=True)
        store_util.save_stores()


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
