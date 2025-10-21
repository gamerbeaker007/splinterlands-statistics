import logging
from threading import Thread

from src.configuration import config, store
from src.pages.main_dash import app
from src.pages.navigation_pages import navigation_page
from src.utils import store_util, update

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    edition_mapping = {
        "alpha": 0,
        "beta": 1,
        "promo": 2,
        "reward": 3,
        "untamed": 4,
        "dice": 5,
        "gladius": 6,
        "chaos": 7,
        "rift": 8,
        "soulbound": 10,
        "rebellion": 12,
        "soulboundrb": 13,
        "conclave": 14,
        "foundations": 15,
        "foundationssb": 16,
    }

    rename_map = {}
    df = store.portfolio
    for col in df.columns:
        for name, eid in edition_mapping.items():
            if col.startswith(f"{name}_"):
                new_col = col.replace(f"{name}_", f"{eid}_", 1)
                rename_map[col] = new_col
                break

    if rename_map:
        store.portfolio = df.rename(columns=rename_map)
        print("Renamed columns:")
        for old, new in rename_map.items():
            print(f"  {old} -> {new}")
    else:
        print("No edition columns found to rename.")
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
