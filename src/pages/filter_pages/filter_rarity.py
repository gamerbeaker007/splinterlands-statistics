import threading

import dash_bootstrap_components as dbc
from dash import Output, Input, ctx, State

from src.pages.main_dash import app
from src.utils.trace_logging import measure_duration
from src.pages.filter_pages import filter_style, filter_page, filter_ids
from src.static.static_values_enum import Rarity


layout = dbc.ButtonGroup(filter_page.get_filter_buttons(Rarity))

for rarity in Rarity:
    @app.callback(
        Output(filter_ids.filter_settings, 'data'),
        Output('{}-filter-button'.format(rarity.name), 'style'),
        Input('{}-filter-button'.format(rarity.name), 'n_clicks'),
        State(filter_ids.filter_settings, 'data'),
        State('{}-filter-button'.format(rarity.name), 'style'),
        prevent_initial_call=True,
    )
    @measure_duration
    def on_click_rarity(n_clicks, filter_settings, style):
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        active = filter_style.is_active(n_clicks)
        filter_settings[setting] = active
        if active:
            style['backgroundColor'] = filter_style.btn_active_color
        else:
            style['backgroundColor'] = filter_style.btn_inactive_color
        return filter_settings, style
