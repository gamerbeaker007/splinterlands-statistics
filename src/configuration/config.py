import os

from src.api import spl
from src.configuration import config_reader

log_level = config_reader.config_logger()
store_dir = os.path.join(os.getcwd(), 'store')
card_details_df = spl.get_card_details()
current_season = spl.get_current_season()
season_end_dates_array = spl.get_season_end_times()
dark_theme = 'cyborg'
light_theme = 'minty'
