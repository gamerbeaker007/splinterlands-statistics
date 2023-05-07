import logging

from src.api import spl
import pandas as pd

from src.configuration import config
from src.dataframe_writter import write_df


def main():
    collections_df = pd.DataFrame()
    for account in config.account_names:
        collection_temp = spl.get_player_collection_df(account)
        collections_df = pd.concat([collections_df, collection_temp])

    write_df(collections_df, 'collection')
    print(config.account_names)


if __name__ == '__main__':
    main()
