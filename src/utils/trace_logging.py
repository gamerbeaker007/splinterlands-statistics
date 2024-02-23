import logging
import time

from dash import ctx

from src.configuration import config


def measure_duration(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time

        if config.trace:
            # Log the duration
            logging.info(f"Function '{func.__name__}' took {duration:.4f}"
                         f" seconds to execute. tigger: '{ctx.triggered_id}'")

        return result

    return wrapper
