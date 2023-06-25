import logging
import os
import sys

from src.api import spl
from src.configuration.custom_formatter import CustomFormatter

file_dir_prefix = ""
# file_dir_prefix = "_new_test_file_"

store_dir = os.path.join(os.getcwd(), 'store', file_dir_prefix)
if not os.path.isdir(store_dir):
    os.mkdir(store_dir)

file_extension = '.csv'

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

