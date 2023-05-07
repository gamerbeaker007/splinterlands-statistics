import json
import logging
import os

from src.api import spl
import pandas as pd

from src.configuration import config


def main():
    collections_df = pd.DataFrame()
    battle_history = pd.DataFrame()
    for account in config.account_names:
        # collections_df = pd.concat([collections_df, spl.get_player_collection_df(account)])
        battle_history = pd.concat([battle_history, spl.get_battle_history_df(account)])


    # bas_dir = os.path.join(os.getcwd(), config.store_dir)
    # file = os.path.join(bas_dir, 'collection.csv')
    # collections_df.to_csv(file)

    # TODO Filter out already process battles

    for index, row in battle_history.iterrows():
        battle_details = json.loads(row.details)
        winner = battle_details['winner']
        team1 = battle_details['team1']
        team2 = battle_details['team2']

        logging.debug('winning team')
        if team1['player'] == winner:
            logging.debug('summoner: ' + str(team1['summoner']['uid']))
            for monster in team1['monsters']:
                logging.debug('monster: ' + str(monster['uid']))
        else:
            logging.debug('summoner: ' + str(team2['summoner']['uid']))
            for monster in team2['monsters']:
                logging.debug('monster: ' + str(monster['uid']))

        logging.debug('losing team')
        if team1['player'] != winner:
            logging.debug('summoner: ' + str(team1['summoner']['uid']))
            for monster in team1['monsters']:
                logging.debug('monster: ' + str(monster['uid']))
        else:
            logging.debug('summoner: ' + str(team2['summoner']['uid']))
            for monster in team2['monsters']:
                logging.debug('monster: ' + str(monster['uid']))


    print(config.account_names)


if __name__ == '__main__':
    main()
