import os

import pandas as pd

from src.configuration import config

battle_big_file = os.path.join(config.store_dir, 'battles_big.csv')
losing_big_file = os.path.join(config.store_dir, 'losing_big.csv')
battle_file = os.path.join(config.store_dir, 'battles.csv')
last_processed_file = os.path.join(config.store_dir, 'last_processed.csv')
collection_file = os.path.join(config.store_dir, 'collection.csv')
rating_file = os.path.join(config.store_dir, 'rating.csv')
season_dec_file = os.path.join(config.store_dir, 'season_dec.csv')
season_merits_file = os.path.join(config.store_dir, 'season_merits.csv')
season_unclaimed_sps_file = os.path.join(config.store_dir, 'season_unclaimed.csv')
season_sps_file = os.path.join(config.store_dir, 'season_sps.csv')
season_vouchers_file = os.path.join(config.store_dir, 'season_vouchers.csv')
season_credits_file = os.path.join(config.store_dir, 'season_credits.csv')

battle_df = pd.DataFrame()
battle_big_df = pd.DataFrame()
losing_big_df = pd.DataFrame()
last_processed_df = pd.DataFrame()
collection_df = pd.DataFrame()
rating_df = pd.DataFrame()
season_dec_df = pd.DataFrame()
season_merits_df = pd.DataFrame()
season_sps_df = pd.DataFrame()
season_unclaimed_sps_df = pd.DataFrame()
season_vouchers_df = pd.DataFrame()
season_credits_df = pd.DataFrame()
