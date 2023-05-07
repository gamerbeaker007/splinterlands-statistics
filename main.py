import json
import logging
import os

from numpy.matlib import ones

from src.api import spl
import pandas as pd

from src.configuration import config


def get_uid(team):
    uid_array = [team['summoner']['uid']]
    logging.debug('summoner: ' + str(team['summoner']['uid']))
    for monster in team['monsters']:
        uid_array.append(monster['uid'])
        logging.debug('monster: ' + str(monster['uid']))
    return uid_array


def update_collection(collections_df, winner_uids, winner):
    # collections_df.loc[winner_uids[0]]
    pass


def main():
    extra_columns = ['wild_win', 'wild_loss', 'modern_win', 'modern_loss', 'total_battles']
    collections_df = pd.DataFrame()
    battle_history = pd.DataFrame()
    for account in config.account_names:
        collections_df = pd.concat([collections_df, spl.get_player_collection_df(account)])
        battle_history = pd.concat([battle_history, spl.get_battle_history_df(account)])

    bas_dir = os.path.join(os.getcwd(), config.store_dir)
    file = os.path.join(bas_dir, 'collection.csv')
    if os.path.isfile(file):
        old_collection = pd.read_csv(file, index_col=[0]).sort_index()

        # Update to new collection from spl
        extra_columns_with_uid = extra_columns.copy()
        extra_columns_with_uid.append('uid')
        old_collection = collections_df.reset_index()\
            .merge(old_collection.reset_index()[extra_columns_with_uid], on='uid', how='left')\
            .set_index('uid')
        old_collection.fillna(0, inplace=True)
        old_collection.sort_index().to_csv(file)
    else:
        collections_df[extra_columns] = 0
        collections_df.sort_index().to_csv(file)

    # combined
    # card | wild_win | wild_loss | modern_win | modern_loss

    # wild
    # card |win | loss
    # modern
    # card | win | loss

    # rulesets
    # ruleset       | card   | win  | loss
    # weak_magic    | card 1 | 1    | 0
    # weak_magic    | card 2 | 2    | 6


    # TODO Filter out already process battles

    for index, row in battle_history.iterrows():
        battle_details = json.loads(row.details)
        winner = battle_details['winner']
        team1 = battle_details['team1']
        team2 = battle_details['team2']

        if team1['player'] == winner:
            logging.debug('winning team' + str(team1['player']))
            winner_uids = get_uid(team1)
        else:
            logging.debug('winning team' + str(team2['player']))
            winner_uids = get_uid(team2)

        logging.debug('losing team')
        if team1['player'] != winner:
            logging.debug('losing team' + str(team1['player']))
            loser_uids = get_uid(team1)
        else:
            logging.debug('losing team' + str(team2['player']))
            loser_uids = get_uid(team2)

        if winner in config.account_names:
            update_collection(collections_df, winner_uids, winner=True)
        else:
            update_collection(collections_df, loser_uids, winner=False)



    print(config.account_names)


if __name__ == '__main__':
    main()
