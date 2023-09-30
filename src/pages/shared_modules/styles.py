from src.configuration import config


def get_server_mode_style():
    if config.server_mode:
        return {'display': 'none'}
    else:
        return {'display': 'block'}
