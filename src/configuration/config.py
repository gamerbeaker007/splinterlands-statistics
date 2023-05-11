import os

from src.api import spl
from src.configuration import config_reader

log_level = config_reader.config_logger()
account_names = config_reader.get_account_names()
store_dir = os.path.join(os.getcwd(), 'store')
card_details_df = spl.get_card_details()

