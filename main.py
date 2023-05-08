import json
import logging
import os

from src.api import spl
import pandas as pd

from src.configuration import config


def get_uid_array(team):
    uid_array = [team['summoner']['uid']]
    logging.debug('summoner: ' + str(team['summoner']['uid']))
    for monster in team['monsters']:
        uid_array.append(monster['uid'])
        logging.debug('monster: ' + str(monster['uid']))
    return uid_array


def update_battle_store(battle_store, team, match_type, match_format, winning):
    uid_arr = get_uid_array(team)
    for uid in uid_arr:

        if match_type == 'Tournament':
            mask = (battle_store['uid'] == uid) \
                   & (battle_store['match_type'] == match_type)
        else:
            mask = (battle_store['uid'] == uid) \
                   & (battle_store['match_type'] == match_type) \
                   & (battle_store['format'] == match_format)


        if mask.any():
            # increase win or loss
            if winning:
                battle_store.loc[mask, 'win'] += 1
            else:
                battle_store.loc[mask, 'loss'] += 1
        else:
            # add new row
            df = pd.DataFrame({'uid': uid,
                               'match_type': match_type,
                               'format': match_format,
                               'win': 1 if winning else 0,
                               'loss': 1 if not winning else 0
                               }, index=[0])
            battle_store = pd.concat([battle_store, df], ignore_index=True)

    return battle_store


def main():
    extra_columns = ['wild_win', 'wild_loss', 'modern_win', 'modern_loss', 'total_battles']
    collections_df = pd.DataFrame()
    for account in config.account_names:
        collections_df = pd.concat([collections_df, spl.get_player_collection_df(account)])

    bas_dir = os.path.join(os.getcwd(), config.store_dir)
    file = os.path.join(bas_dir, 'collection.csv')
    if os.path.isfile(file):
        old_collection = pd.read_csv(file, index_col=[0]).sort_index()

        # Update to new collection from spl
        extra_columns_with_uid = extra_columns.copy()
        extra_columns_with_uid.append('uid')
        old_collection = collections_df.reset_index() \
            .merge(old_collection.reset_index()[extra_columns_with_uid], on='uid', how='left') \
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

    battle_store_file = os.path.join(bas_dir, 'battles.csv')
    if os.path.isfile(battle_store_file):
        battle_store = pd.read_csv(battle_store_file, index_col=0)
        battle_store = battle_store.where(battle_store.notnull(), None)
    else:
        battle_store = pd.DataFrame(columns=['uid', 'match_type', 'format', 'win', 'loss'])

    last_processed_file = os.path.join(bas_dir, 'last_processed.csv')
    if os.path.isfile(last_processed_file):
        last_processed = pd.read_csv(last_processed_file, index_col=0)
    else:
        last_processed = pd.DataFrame(columns=['account', 'last_processed'])

    for account in config.account_names:
        battle_history = spl.get_battle_history_df(account)

        if not last_processed.loc[(last_processed.account == account)].empty:
            # filter out already processed
            last_processed_date = last_processed.loc[(last_processed.account == account)].last_processed.values[0]
            battle_history = battle_history.loc[(battle_history['created_date'] > last_processed_date)]
        if not battle_history.empty:
            for index, row in battle_history.iterrows():
                match_type = row['match_type']
                match_format = row['format']

                battle_details = json.loads(row.details)
                if not ('type' in battle_details and battle_details['type'] == 'Surrender'):
                    winner = battle_details['winner']

                    if battle_details['team1']['player'] == account:
                        my_team = battle_details['team1']
                        opponent_team = battle_details['team2']
                    else:
                        my_team = battle_details['team2']
                        opponent_team = battle_details['team1']

                    if winner == account:
                        logging.debug('Battle Won ')
                        battle_store = update_battle_store(battle_store, my_team, match_type, match_format, winning=True)
                    else:
                        logging.debug('Battle Lost ')
                        battle_store = update_battle_store(battle_store, my_team, match_type, match_format, winning=False)
                        # add_losing_card_tracking(losing_battle_store, opponent_team, match_type, match_format)
                else:
                    logging.debug("Surrender match skipp")

            # save last_process
            last_processed_date = battle_history.sort_values(by='created_date', ascending=False)['created_date'].iloc[0]
            if last_processed.loc[(last_processed.account == account)].empty:
                # create
                new = pd.DataFrame({'account': [account], 'last_processed': [last_processed_date]}, index=[0])
                last_processed = pd.concat([last_processed, new], ignore_index=True)
            else:
                last_processed.loc[(last_processed.account == account), 'last_processed'] = last_processed_date
        else:
            logging.debug('No battle to process anymore')

    #save battle store
    last_processed.sort_index().to_csv(last_processed_file)


    #save battle store
    battle_store.sort_index().to_csv(battle_store_file)

    print(config.account_names)


if __name__ == '__main__':
    main()
