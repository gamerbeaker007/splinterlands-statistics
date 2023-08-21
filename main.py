import logging

from src.api import spl
from src.configuration import store, config
from src.pages.navigation_pages import navigation_page
from src.pages.main_dash import app
from src.static.static_values_enum import Format
from src.utils import store_util

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    if not store.battle_big.empty:
        store.battle_big.loc[store.battle_big.card_name == 'Zyriel', 'secondary_color'] = 'Black'

        battle_id_to_process = store.battle_big.loc[(store.battle_big['format'].isna())].battle_id.unique().tolist()
        counter = 0
        for battle_id in battle_id_to_process:
            battle = spl.get_battle(battle_id)
            if 'format' in battle:
                battle_format = battle['format']
                if not battle_format:
                    battle_format = Format.wild.value
                print("Migrate battles (format) " + str(counter) + " / " + str(len(battle_id_to_process)))
                counter += 1
                store.battle_big.loc[store.battle_big.battle_id == battle_id, 'format'] = battle_format

        if 'opponent' not in store.battle_big.columns.tolist():
            battle_id_to_process = store.battle_big.battle_id.unique().tolist()
            counter = 0
            for battle_id in battle_id_to_process:
                battle = spl.get_battle(battle_id)
                account = store.battle_big.loc[store.battle_big.battle_id == battle_id].account.tolist()[0]
                opponent = battle['player_2'] if battle['player_1'] == account else battle['player_1']
                store.battle_big.loc[store.battle_big.battle_id == battle_id, 'opponent'] = opponent
                print("Migrate battles (opponent) " + str(counter) + " / " + str(len(battle_id_to_process)))
                counter += 1

            # Reorder columns
            store.battle_big = store.battle_big[
                ['card_detail_id', 'card_name', 'card_type', 'rarity', 'color', 'secondary_color', 'xp', 'gold',
                 'level', 'edition', 'account', 'opponent', 'created_date', 'match_type', 'format', 'mana_cap',
                 'ruleset1', 'ruleset2', 'ruleset3', 'inactive', 'battle_id', 'winner', 'result']]

        if not store.losing_big.empty:
            store.losing_big.loc[store.losing_big.card_name == 'Zyriel', 'secondary_color'] = 'Black'

            battle_id_to_process = store.losing_big.loc[(store.losing_big['format'].isna())].battle_id.unique().tolist()
            counter = 0
            for battle_id in battle_id_to_process:
                battle = spl.get_battle(battle_id)
                if 'format' in battle:
                    battle_format = battle['format']
                    if not battle_format:
                        battle_format = Format.wild.value
                    print("Migrate losing battles (format) " + str(counter) + " / " + str(len(battle_id_to_process)))
                    counter += 1
                    store.losing_big.loc[store.losing_big.battle_id == battle_id, 'format'] = battle_format

            battle_id_to_process = store.losing_big.loc[(store.losing_big['opponent'] == 'DRAW')].battle_id.unique().tolist()
            counter = 0
            for battle_id in battle_id_to_process:
                battle = spl.get_battle(battle_id)
                account = store.losing_big.loc[store.losing_big.battle_id == battle_id].account.tolist()[0]
                opponent = battle['player_2'] if battle['player_1'] == account else battle['player_1']
                store.losing_big.loc[store.losing_big.battle_id == battle_id, 'opponent'] = opponent
                print("Migrate battles (FIX DRAW BATTLES) " + str(counter) + " / " + str(len(battle_id_to_process)))
                counter += 1

    store_util.save_stores()


def main():
    migrate_data()

    app.layout = navigation_page.layout
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', debug=config.debug)


if __name__ == '__main__':
    main()
