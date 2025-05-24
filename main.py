import logging
from threading import Thread

from src.configuration import config, store
from src.pages.main_dash import app
from src.pages.navigation_pages import navigation_page
from src.utils import store_util, update

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    name_map = {
        "Black Dragon": "Korjack",
        "Void Dragon": "Voidmaw",
        "Gem Meteor": "Etherite Construct",
    }

    def needs_migration(df):
        if df.empty:
            return False

        old_names_present = df['card_name'].isin(name_map.keys()).any()
        fiend_present = df['card_name'].str.contains(r'\bFiend\b', regex=True).any()
        silenced_summoners_present = df[['ruleset1', 'ruleset2', 'ruleset3']].isin(['Silenced Summoners']).any().any()

        return old_names_present or fiend_present or silenced_summoners_present

    def apply_migrations(df):
        df['card_name'] = df['card_name'].replace(name_map)
        df['card_name'] = df['card_name'].str.replace(r'\bFiend\b', 'Spawn', regex=True)

        for col in ['ruleset1', 'ruleset2', 'ruleset3']:
            df[col] = df[col].replace('Silenced Summoners', 'Silenced Archons')

    if needs_migration(store.battle_big):
        apply_migrations(store.battle_big)
        store_util.save_stores()

    if needs_migration(store.losing_big):
        apply_migrations(store.losing_big)
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
