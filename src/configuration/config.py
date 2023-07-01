import logging
import os
import sys

from src.api import spl
from src.configuration.custom_formatter import CustomFormatter

# config logger
root_logger = logging.getLogger()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomFormatter())
root_logger.addHandler(console_handler)

log_level = os.environ.get("LOG_LEVEL")
if not log_level:
    log_level = "INFO"

root_logger.setLevel(log_level)
logging.info("Set log level: " + log_level)

card_details_df = spl.get_card_details()
current_season = spl.get_current_season()
settings = spl.get_settings()
dark_theme = 'cyborg'
light_theme = 'minty'
current_theme = dark_theme

debug_env = os.environ.get("DEBUG")
store_prefix_env = os.environ.get("STORE")

debug = False
if debug_env:
    logging.info("Debug environment variable found using debug: " + str(debug_env))
    debug = debug_env

file_dir_prefix = ""
if store_prefix_env:
    logging.info("Store prefix environment variable found using store dir: " + str(store_prefix_env))
    file_dir_prefix = store_prefix_env

store_dir = os.path.join(os.getcwd(), 'store', file_dir_prefix)
if not os.path.isdir(store_dir):
    os.mkdir(store_dir)

file_extension = '.csv'
