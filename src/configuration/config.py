import argparse
import logging
import os
import sys

from src.api import spl
from src.configuration import standalone_version
from src.configuration.custom_formatter import CustomFormatter

parser = argparse.ArgumentParser(description='A sample program with command line arguments.')
parser.add_argument('-d', '--debug',
                    action='store_true',
                    help='Enable debug mode')
parser.add_argument('-t', '--trace',
                    action='store_true',
                    help='This will enable trace logging (durations)')
parser.add_argument('-l', '--log-level',
                    choices=['WARN', 'ERR', 'DEBUG', 'INFO'],
                    default='INFO', help='Set log level')
parser.add_argument('-s', '--server-mode',
                    action='store_true',
                    help='Enable server mode')
parser.add_argument('-st', '--store',
                    default='',
                    help='Specify a store')
parser.add_argument('-ro', '--read-only',
                    action='store_true',
                    help='Read only')

if os.getenv('APP_VERSION'):
    APP_VERSION = os.getenv('APP_VERSION')
else:
    APP_VERSION = standalone_version.__standalone_version__

args = parser.parse_args()

# config logger
root_logger = logging.getLogger()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomFormatter())
root_logger.addHandler(console_handler)
root_logger.setLevel(args.log_level)
logging.info('Log level:' + str(args.log_level))
logging.info('Debug mode:' + str(args.debug))
logging.info('Trace mode:' + str(args.trace))
logging.info('Server mode:' + str(args.server_mode))
logging.info('Read only mode:' + str(args.read_only))

trace = args.trace
debug = args.debug
file_dir_prefix = args.store
server_mode = args.server_mode
read_only = args.read_only

if file_dir_prefix:
    logging.info('Store variable found using store dir: ' + str(args.store))

store_dir = os.path.join(os.getcwd(), 'store', file_dir_prefix)
if not os.path.isdir(store_dir):
    os.mkdir(store_dir)

card_details_df = spl.get_card_details()
settings = spl.get_settings()
dark_theme = 'slate'
light_theme = 'minty'
current_theme = dark_theme
file_extension = '.csv'
