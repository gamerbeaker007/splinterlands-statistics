import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, ctx, State

from main import app, measure_duration
from src.pages.filter_pages import filter_style, filter_page, filter_ids
from src.static.static_values_enum import Element

filter_settings_lock = threading.Lock()

layout = dbc.ButtonGroup(filter_page.get_filter_buttons(Element))

for element in Element:
    @app.callback(
        Output(filter_ids.filter_settings, 'data'),
        Output('{}-filter-button'.format(element.name), 'style'),
        Input('{}-filter-button'.format(element.name), 'n_clicks'),
        State(filter_ids.filter_settings, 'data'),
        State('{}-filter-button'.format(element.name), 'style'),
        prevent_initial_call=True,
    )
    @measure_duration
    def on_click_element(n_clicks, filter_settings, style):
        # Acquire the lock before updating the shared resource
        with filter_settings_lock:
            setting = ctx.inputs_list[0]['id'].split('-')[0]
            active = filter_style.is_active(n_clicks)
            filter_settings[setting] = active
            if active:
                style['backgroundColor'] = filter_style.btn_active_color
            else:
                style['backgroundColor'] = filter_style.btn_inactive_color
            return filter_settings, style
