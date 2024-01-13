import dash_bootstrap_components as dbc
from dash import Output, Input, ctx, State

from src.pages.filter_pages import filter_style, filter_page, filter_ids
from src.pages.main_dash import app
from src.static.static_values_enum import Format
from src.utils.trace_logging import measure_duration

layout = dbc.ButtonGroup(filter_page.get_filter_buttons(Format))

for battle_format in Format:
    @app.callback(
        Output(filter_ids.filter_settings, 'data'),
        Output('{}-filter-button'.format(battle_format.name), 'className'),
        Input('{}-filter-button'.format(battle_format.name), 'n_clicks'),
        State(filter_ids.filter_settings, 'data'),
        prevent_initial_call=True,
    )
    @measure_duration
    def on_click_battle_format(n_clicks, filter_settings):
        setting = ctx.inputs_list[0]['id'].split('-')[0]
        active = filter_style.is_active(n_clicks)
        filter_settings[setting] = active

        return filter_settings, filter_style.determine_class(active)
