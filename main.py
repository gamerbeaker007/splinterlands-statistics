import logging

from src.configuration import store, config
from src.pages import navigation_page
from src.pages.main_dash import app
from src.utils import store_util

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    if not store.battle_big.empty and 'card_rarity' not in store.battle_big.columns.to_list():
        store.battle_big['rarity'] = store.battle_big.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['rarity'], axis=1)
        columns_order = ['card_detail_id', 'card_name', 'card_type', 'rarity', 'color', 'secondary_color', 'xp', 'gold',
                         'level', 'edition', 'account', 'created_date', 'match_type', 'format', 'mana_cap', 'ruleset1',
                         'ruleset2', 'ruleset3', 'inactive', 'battle_id', 'winner', 'result']
        store.battle_big = store.battle_big[columns_order]
    if not store.losing_big.empty and 'card_rarity' not in store.battle_big.columns.to_list():
        store.losing_big['rarity'] = store.losing_big.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['rarity'], axis=1)
        columns_order = ['card_detail_id', 'card_name', 'card_type', 'rarity', 'color', 'secondary_color', 'xp', 'gold',
                         'level', 'edition', 'account', 'created_date', 'match_type', 'format', 'mana_cap', 'ruleset1',
                         'ruleset2', 'ruleset3', 'inactive', 'battle_id', 'opponent']
        store.losing_big = store.losing_big[columns_order]

    store_util.save_stores()


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
