import os

import pandas as pd

from src.configuration import config

battle_big_file = os.path.join(config.store_dir, 'battles_big.csv')
losing_big_file = os.path.join(config.store_dir, 'losing_big.csv')
battle_file = os.path.join(config.store_dir, 'battles.csv')
last_processed_file = os.path.join(config.store_dir, 'last_processed.csv')
collection_file = os.path.join(config.store_dir, 'collection.csv')
rating_file = os.path.join(config.store_dir, 'rating.csv')

battle_df = pd.DataFrame()
battle_big_df = pd.DataFrame()
losing_big_df = pd.DataFrame()
last_processed_df = pd.DataFrame()
collection_df = pd.DataFrame()
rating_df = pd.DataFrame()
