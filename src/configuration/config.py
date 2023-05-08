import os

from src.configuration import config_reader

log_level = config_reader.config_logger()
account_names = config_reader.get_account_names()
store_dir = os.path.join(os.getcwd(), 'store')
