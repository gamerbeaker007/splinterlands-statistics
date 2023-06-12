import json
import logging

import pandas as pd

from src.api import spl
from src.configuration import config, store
from src.static.static_values_enum import MatchType, Format
from src.utils import store_util, progress_util


def get_uid_array(team):
    uid_array = [team['summoner']['uid']]
    for monster in team['monsters']:
        uid_array.append(monster['uid'])
    return uid_array


def update_battle_store_card_specific(account, team, battle):
    match_type = battle['match_type']
    match_format = battle['format']
    win = True if battle['winner'] == account else False

    empty = store.battle.empty
    mask = (False)
    uid_arr = get_uid_array(team)
    for uid in uid_arr:

        if not empty:
            if match_type == 'Tournament':
                mask = (store.battle['uid'] == uid) \
                       & (store.battle['match_type'] == match_type)
            else:
                mask = (store.battle['uid'] == uid) \
                       & (store.battle['match_type'] == match_type) \
                       & (store.battle['format'] == match_format)

        if not empty and mask.any():
            # increase win or loss
            if win:
                store.battle.loc[mask, 'win'] += 1
            else:
                store.battle.loc[mask, 'loss'] += 1
        else:
            # add new row
            df = pd.DataFrame({'uid': uid,
                               'account': account,
                               'match_type': match_type,
                               'format': match_format,
                               'win': 1 if win else 0,
                               'loss': 1 if not win else 0
                               }, index=[0])
            store.battle = pd.concat([store.battle, df], ignore_index=True)


def add_battle_store_big_my(account, team, battle):
    match_type = battle['match_type']
    match_format = battle['format']
    created_date = battle['created_date']
    mana_cap = battle['mana_cap']
    rulesets = battle['ruleset']
    inactive = battle['inactive']
    battle_id = battle['battle_queue_id_1']
    winner = battle['winner']
    result = "win" if winner == account else "loss"


    cards = list(team['monsters'])
    cards.append(team['summoner'])
    ruleset_split = ['None', 'None', 'None']
    for idx, ruleset in enumerate(rulesets.split('|')):
        ruleset_split[idx] = ruleset

    for card in cards:
        # add new row
        card_id = card['card_detail_id']
        card_name = config.card_details_df.loc[card_id]['name']
        df = pd.DataFrame({'card_detail_id': card_id,
                           'card_name': card_name,
                           'card_type': config.card_details_df.loc[card_id]['type'],
                           'color': config.card_details_df.loc[card_id]['color'],
                           'secondary_color': config.card_details_df.loc[card_id]['secondary_color'],
                           'xp': card['xp'],
                           'gold': card['gold'],
                           'level': card['level'],
                           'edition': card['edition'],
                           'account': account,
                           'created_date': created_date,
                           'match_type': match_type,
                           'format': match_format,
                           'mana_cap': mana_cap,
                           'ruleset1': ruleset_split[0],
                           'ruleset2': ruleset_split[1],
                           'ruleset3': ruleset_split[2],
                           'inactive': inactive,
                           'battle_id': battle_id,
                           'winner': winner,
                           'result': result,
                           }, index=[0])
        store.battle_big = pd.concat([store.battle_big, df], ignore_index=True)


def log_battle_note(count):
    limit = 50
    if count == limit:
        logging.info(str(limit) + ' or more battles to process consider running this program more often')
        logging.info('SPL API limits ' + str(limit) + ' battle history')
    else:
        logging.info(str(count) + ' battles to process')


def add_rating_log(account, battle):
    if battle['player_1'] == account:
        final_rating = battle['player_1_rating_final']
    else:
        final_rating = battle['player_2_rating_final']

    # format = null when wild
    if battle['format']:
        match_format = battle['format']
    else:
        match_format = Format.WILD.value

    df = pd.DataFrame({'created_date': battle['created_date'],
                       'account': account,
                       'rating': final_rating,
                       'format': match_format,
                       }, index=[0])
    store.rating = pd.concat([store.rating, df], ignore_index=True)


def add_losing_battle_team(account, team, battle):
    match_type = battle['match_type']
    match_format = battle['format']
    created_date = battle['created_date']
    mana_cap = battle['mana_cap']
    rulesets = battle['ruleset']
    inactive = battle['inactive']
    battle_id = battle['battle_queue_id_1']
    opponent = battle['winner']

    cards = list(team['monsters'])
    cards.append(team['summoner'])
    ruleset_split = ['None', 'None', 'None']
    for idx, ruleset in enumerate(rulesets.split('|')):
        ruleset_split[idx] = ruleset

    for card in cards:
        # add new row
        card_id = card['card_detail_id']
        card_name = config.card_details_df.loc[card_id]['name']
        df = pd.DataFrame({'card_detail_id': card_id,
                           'card_name': card_name,
                           'card_type': config.card_details_df.loc[card_id]['type'],
                           'color': config.card_details_df.loc[card_id]['color'],
                           'secondary_color': config.card_details_df.loc[card_id]['secondary_color'],
                           'xp': card['xp'],
                           'gold': card['gold'],
                           'level': card['level'],
                           'edition': card['edition'],
                           'account': account,
                           'created_date': created_date,
                           'match_type': match_type,
                           'format': match_format,
                           'mana_cap': mana_cap,
                           'ruleset1': ruleset_split[0],
                           'ruleset2': ruleset_split[1],
                           'ruleset3': ruleset_split[2],
                           'inactive': inactive,
                           'battle_id': battle_id,
                           'opponent': opponent,
                           }, index=[0])
        store.losing_big = pd.concat([store.losing_big, df], ignore_index=True)


def get_battles_to_process(account):
    battle_history = spl.get_battle_history_df(account)
    if not store.last_processed.empty and \
            not store.last_processed.loc[(store.last_processed.account == account)].empty:
        # filter out already processed
        last_processed_date = \
            store.last_processed.loc[(store.last_processed.account == account)].last_processed.values[0]
        battle_history = battle_history.loc[(battle_history['created_date'] > last_processed_date)]
    return battle_history


def process_battle(account):
    battle_history = get_battles_to_process(account)

    log_battle_note(len(battle_history.index))

    if not battle_history.empty:
        for index, battle in battle_history.iterrows():
            match_type = battle['match_type']

            battle_details = json.loads(battle.details)
            if not is_surrender(battle_details):
                winner_name = battle_details['winner']

                if battle_details['team1']['player'] == account:
                    my_team = battle_details['team1']
                    opponent_team = battle_details['team2']
                else:
                    my_team = battle_details['team2']
                    opponent_team = battle_details['team1']

                add_battle_store_big_my(account,
                                        my_team,
                                        battle)
                update_battle_store_card_specific(account,
                                                  my_team,
                                                  battle)

                # If a ranked match also log the rating
                if match_type and match_type == MatchType.RANKED.value:
                    add_rating_log(account, battle)

                # If the battle is lost store losing battle
                if winner_name != account:
                    add_losing_battle_team(account,
                                           opponent_team,
                                           battle)
            else:
                logging.debug("Surrender match skip")

        last_processed_date = battle_history.sort_values(by='created_date', ascending=False)['created_date'].iloc[0]
        update_last_processed_df(account, last_processed_date)
    else:
        logging.debug('No battles to process.')


def update_last_processed_df(account, last_processed_date):
    if store.last_processed.empty or store.last_processed.loc[(store.last_processed.account == account)].empty:
        # create
        new = pd.DataFrame({'account': [account],
                            'last_processed': [last_processed_date]},
                           index=[0])
        store.last_processed = pd.concat([store.last_processed, new], ignore_index=True)
    else:
        store.last_processed.loc[(store.last_processed.account == account),
        'last_processed'] = last_processed_date


def is_surrender(battle_details):
    return 'type' in battle_details and battle_details['type'] == 'Surrender'


def process_battles():
    progress_util.update_daily_msg("Start processing battles")
    for account in store_util.get_account_names():
        progress_util.update_daily_msg("...processing: " + account)
        process_battle(account)
