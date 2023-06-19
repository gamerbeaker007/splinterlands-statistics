import logging

from src.configuration import store
from src.pages import navigation_page
from src.pages.main_dash import app
from src.utils import store_util

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    pass
    # store.battle_big = store.battle_big.card_type.str.lower()
    # store.losing_big = store.losing_big.card_type.str.lower()
    # store_util.save_stores()


def main():
    migrate_data()
    # balances_info.get_balances()
    # collection_store.update_collection()
    # battle_store.process_battles()
    #
    # store_util.save_stores()
    # portfolio.update_portfolios()

    app.layout = navigation_page.layout
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
