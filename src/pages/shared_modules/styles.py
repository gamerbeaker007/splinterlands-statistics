from src.configuration import config


def get_server_mode_style():
    if config.server_mode:
        return {'display': 'none'}
    else:
        return {'display': 'block'}


def get_read_only_mode_style():
    if config.read_only:
        return {'display': 'none'}
    else:
        return {'display': 'block'}
