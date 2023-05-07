import logging
import os

from src.api import spl
import pandas as pd

from src.configuration import config


def main():
    collections_df = pd.DataFrame()
    battle_history = pd.DataFrame()
    for account in config.account_names:
        collections_df = pd.concat([collections_df, spl.get_player_collection_df(account)])
        battle_history = pd.concat([battle_history, spl.get_battle_history_df(account)])


    bas_dir = os.path.join(os.getcwd(), config.store_dir)
    file = os.path.join(bas_dir, 'collection.csv')
    collections_df.to_csv(file)


    print(config.account_names)


if __name__ == '__main__':
    main()
