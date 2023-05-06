import configparser
import logging
import os
import sys

from src.configuration.custom_formatter import CustomFormatter

config = configparser.RawConfigParser()
config.read('config.properties')


class Configuration(object):
    instance = None
    account_names = None
    log_level = None
    store_dir = 'store'

    def __new__(cls):
        """ creates a singleton object, if it is not created,
        or else returns the previous singleton object"""
        if cls.instance is None:
            cls.instance = super(Configuration, cls).__new__(cls)
            cls.log_level = config_logger()
            cls.account_names = load_account_names()
        return cls.instance


def load_account_names():
    account_names_str = os.environ.get("ACCOUNT_NAMES")
    if not account_names_str:
        logging.debug("No environment ACCOUNT_NAMES found, using default from config.properties")
        account_names_str = config.get('settings', 'account_names')

    account_names = account_names_str.split(',')
    logging.info("Using account(s): " + ', '.join(account_names))
    Configuration().account_names = account_names
    return account_names


def config_logger():
    root_logger = logging.getLogger()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(console_handler)

    log_level = os.environ.get("LOG_LEVEL")
    if not log_level:
        log_level = config.get('settings', 'log_level')
        root_logger.setLevel(log_level)
        logging.debug("No environment LOG_LEVEL found, using default from config.properties")

    root_logger.setLevel(log_level)
    logging.info("Set log level: " + log_level)
    return log_level
