from src.configuration import config

btn_active_color_dark = '#222'
btn_inactive_color_dark = '#01131B'

btn_active_color_light = '#006969'
btn_inactive_color_light = '#78C2AD'


def button_get_inactive_color():
    return btn_inactive_color_dark if config.current_theme == config.dark_theme else btn_inactive_color_light


def button_get_active_color():
    return btn_active_color_dark if config.current_theme == config.dark_theme else btn_active_color_light


def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False


def determine_background_color(style):
    if 'backgroundColor' in style and (style['backgroundColor'] == btn_active_color_dark
                                       or style['backgroundColor'] == btn_active_color_light):
        style['backgroundColor'] = button_get_active_color()
    else:
        style['backgroundColor'] = button_get_inactive_color()
    return style
