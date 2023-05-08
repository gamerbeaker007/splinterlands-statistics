import json
import logging

import pandas as pd

from src.api import spl
from src.configuration import config, store


def get_uid_array(team):
    uid_array = [team['summoner']['uid']]
    for monster in team['monsters']:
        uid_array.append(monster['uid'])
    return uid_array


def update_battle_store(team, match_type, match_format, winning):
    uid_arr = get_uid_array(team)
    for uid in uid_arr:

        if match_type == 'Tournament':
            mask = (store.battle_df['uid'] == uid) \
                   & (store.battle_df['match_type'] == match_type)
        else:
            mask = (store.battle_df['uid'] == uid) \
                   & (store.battle_df['match_type'] == match_type) \
                   & (store.battle_df['format'] == match_format)

        if mask.any():
            # increase win or loss
            if winning:
                store.battle_df.loc[mask, 'win'] += 1
            else:
                store.battle_df.loc[mask, 'loss'] += 1
        else:
            # add new row
            df = pd.DataFrame({'uid': uid,
                               'match_type': match_type,
                               'format': match_format,
                               'win': 1 if winning else 0,
                               'loss': 1 if not winning else 0
                               }, index=[0])
            store.battle_df = pd.concat([store.battle_df, df], ignore_index=True)


def add_battle_log(created_date, mana_cap, team, match_type, match_format, ruleset, inactive, result):
    uid_arr = get_uid_array(team)
    for uid in uid_arr:
            # add new row
            df = pd.DataFrame({'uid': uid,
                               'created_date': created_date,
                               'match_type': match_type,
                               'format': match_format,
                               'mana_cap': mana_cap,
                               'ruleset': ruleset,
                               'inactive': inactive,
                               'result': result,
                               }, index=[0])
            store.battle_big_df = pd.concat([store.battle_big_df, df], ignore_index=True)



def process_battle(account):
    battle_history = spl.get_battle_history_df(account)
    if not store.last_processed_df.loc[(store.last_processed_df.account == account)].empty:
        # filter out already processed
        last_processed_date = store.last_processed_df.loc[(store.last_processed_df.account == account)].last_processed.values[0]
        battle_history = battle_history.loc[(battle_history['created_date'] > last_processed_date)]

    if not battle_history.empty:
        for index, row in battle_history.iterrows():
            match_type = row['match_type']
            match_format = row['format']
            created_date = row['created_date']
            mana_cap = row['mana_cap']
            ruleset = row['ruleset']
            inactive = row['inactive']

            battle_details = json.loads(row.details)
            if not ('type' in battle_details and battle_details['type'] == 'Surrender'):
                winner = battle_details['winner']

                if battle_details['team1']['player'] == account:
                    my_team = battle_details['team1']
                    opponent_team = battle_details['team2']
                else:
                    my_team = battle_details['team2']
                    opponent_team = battle_details['team1']

                    add_battle_log(created_date,
                                   mana_cap,
                                   my_team,
                                   match_type,
                                   match_format,
                                   ruleset,
                                   inactive,
                                   "win" if winner == account else "loss")
                if winner == account:
                    logging.debug('Battle Won')
                    update_battle_store(my_team, match_type, match_format, winning=True)

                else:
                    logging.debug('Battle Lost')
                    update_battle_store(my_team, match_type, match_format, winning=False)
                    # add_losing_card_tracking(losing_battle_store, opponent_team, match_type, match_format)
            else:
                logging.debug("Surrender match skip")

        # save last_process
        last_processed_date = battle_history.sort_values(by='created_date', ascending=False)['created_date'].iloc[0]
        if store.last_processed_df.loc[(store.last_processed_df.account == account)].empty:
            # create
            new = pd.DataFrame({'account': [account], 'last_processed': [last_processed_date]}, index=[0])
            store.last_processed_df = pd.concat([store.last_processed_df, new], ignore_index=True)
        else:
            store.last_processed_df.loc[(store.last_processed_df.account == account), 'last_processed'] = last_processed_date
    else:
        logging.debug('No battles to process.')


def process_battles():
    logging.info("Start processing battles")
    for account in config.account_names:
        logging.info("...processing: " + account)
        process_battle(account)
    logging.info("End processing battles")
