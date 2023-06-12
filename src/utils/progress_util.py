import logging

from src.configuration import progress


def update_season_msg(msg):
    logging.info(msg)
    progress.progress_season_txt = msg


def set_daily_title(title):
    progress.progress_daily_title = title


def update_daily_msg(msg):
    logging.info(msg)
    progress.progress_daily_txt = msg
