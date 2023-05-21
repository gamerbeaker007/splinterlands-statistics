import configparser
import logging
import os
import sys

from src.configuration.custom_formatter import CustomFormatter

config_parser = configparser.RawConfigParser()
config_parser.read('config.properties')


def config_logger():
    root_logger = logging.getLogger()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)

    level = os.environ.get("LOG_LEVEL")
    if not level:
        level = config_parser.get('settings', 'log_level')
        root_logger.setLevel(level)
        logging.debug("No environment LOG_LEVEL found, using default from config.properties")

    root_logger.setLevel(level)
    logging.info("Set log level: " + level)
    return level


