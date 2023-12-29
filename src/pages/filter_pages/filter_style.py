btn_active_color = '#222'
btn_inactive_color = '#bdbfbe'


def is_active(n_clicks):
    return n_clicks % 2 == 1 if n_clicks else False


def determine_style(filter_settings, style, style_id):
    style['backgroundColor'] = btn_inactive_color
    if style_id in filter_settings:
        if filter_settings[style_id]:
            style['backgroundColor'] = btn_active_color
    return style
