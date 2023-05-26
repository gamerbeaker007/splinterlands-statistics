import os

import pandas as pd

from src.api import spl
from src.configuration import config_reader

DEBUG_FILES = False
log_level = config_reader.config_logger()
store_dir = os.path.join(os.getcwd(), 'store')
card_details_df = spl.get_card_details()
current_season = spl.get_current_season()
# season_end_dates_array = spl.get_season_end_times()
dark_theme = 'cyborg'
light_theme = 'minty'
current_theme = dark_theme

file_prefix = ""
if DEBUG_FILES:
    file_prefix = "_test_file_"

file_extension = '.csv'

# class Stores:
#     def __init__(self):
#         self.accounts = 'accounts'
#         self.battles_big = 'battles_big'
#         self.losing_big = 'losing_big'
#         self.battles = 'battles'
#         self.last_processed = 'last_processed'
#         self.collection = 'collection'
#         self.rating = 'rating'
#         self.season_dec = 'season_dec'
#         self.season_merits = 'season_merits'
#         self.season_unclaimed = 'season_unclaimed'
#         self.season_sps = 'season_sps'
#         self.season_vouchers = 'season_vouchers'
#         self.season_credits = 'season_credits'
#         self.season_end_dates = 'season_end_dates'
#         self.season_modern_battle_info = 'season_modern_battle_info'
#         self.season_wild_battle_info = 'season_wild_battle_info'
