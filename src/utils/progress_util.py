import logging

from src.configuration import progress


def set_msg(msg):
    logging.info(msg)
    progress.progress_txt = msg


def set_battle_msg(msg):
    logging.info(msg)
    progress.progress_battle_txt = msg
