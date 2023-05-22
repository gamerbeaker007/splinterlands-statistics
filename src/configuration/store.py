import os

import pandas as pd

from src.configuration import config

prefix_file = ""
if config.DEBUG_FILES:
    prefix_file = "_test_file_"

accounts_file = os.path.join(config.store_dir, str(prefix_file) + ' accounts.csv')
battle_big_file = os.path.join(config.store_dir, str(prefix_file) + ' battles_big.csv')
losing_big_file = os.path.join(config.store_dir, str(prefix_file) + ' losing_big.csv')
battle_file = os.path.join(config.store_dir, str(prefix_file) + ' battles.csv')
last_processed_file = os.path.join(config.store_dir, str(prefix_file) + ' last_processed.csv')
collection_file = os.path.join(config.store_dir, str(prefix_file) + ' collection.csv')
rating_file = os.path.join(config.store_dir, str(prefix_file) + ' rating.csv')
season_dec_file = os.path.join(config.store_dir, str(prefix_file) + ' season_dec.csv')
season_merits_file = os.path.join(config.store_dir, str(prefix_file) + ' season_merits.csv')
season_unclaimed_sps_file = os.path.join(config.store_dir, str(prefix_file) + ' season_unclaimed.csv')
season_sps_file = os.path.join(config.store_dir, str(prefix_file) + ' season_sps.csv')
season_vouchers_file = os.path.join(config.store_dir, str(prefix_file) + ' season_vouchers.csv')
season_credits_file = os.path.join(config.store_dir, str(prefix_file) + ' season_credits.csv')
season_end_dates_file = os.path.join(config.store_dir, str(prefix_file) + ' season_end_dates.csv')

season_end_dates_df = pd.DataFrame()
accounts_df = pd.DataFrame()
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


