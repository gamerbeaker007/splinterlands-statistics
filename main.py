from src.configuration import store, config
from src.pages import navigation_page
from src.pages.main_dash import app
from src.utils import store_util

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    if (not store.battle_big_df.empty) and ('color' not in store.battle_big_df.columns.to_list()):
        store.battle_big_df['color'] = store.battle_big_df.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['color'], axis=1)
        store.battle_big_df['secondary_color'] = store.battle_big_df.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['secondary_color'], axis=1)
        store.battle_big_df = store.battle_big_df[['card_detail_id', 'card_name', 'card_type', 'color', 'secondary_color', 'xp', 'gold', 'level', 'edition', 'account', 'created_date', 'match_type', 'format', 'mana_cap', 'ruleset1', 'ruleset2', 'ruleset3', 'inactive', 'battle_id', 'winner', 'result']]

    if (not store.losing_big_df.empty) and ('color' not in store.losing_big_df.columns.to_list()):
        store.losing_big_df['color'] = store.losing_big_df.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['color'], axis=1)
        store.losing_big_df['secondary_color'] = store.losing_big_df.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['secondary_color'], axis=1)
        store.losing_big_df = store.losing_big_df[['card_detail_id', 'card_name', 'card_type', 'color', 'secondary_color', 'xp', 'gold', 'level', 'edition', 'account', 'created_date',
         'match_type', 'format', 'mana_cap', 'ruleset1', 'ruleset2', 'ruleset3', 'inactive', 'battle_id', 'opponent']]
    store_util.save_stores()


def main():
    migrate_data()
    # balances_info.get_balances()
    # collection_store.update_collection()
    # battle_store.process_battles()
    #
    # store_util.save_stores()

    app.layout = navigation_page.layout
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
