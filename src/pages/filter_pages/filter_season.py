import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State

from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.utils import season_util
from src.utils.trace_logging import measure_duration

date_fmt = '%Y-%m-%d %H:%M (UTC)'

layout = dbc.InputGroup(
    [
        dbc.InputGroupText('Since season'),
        dcc.Dropdown(id=filter_ids.filter_season_dropdown,
                     clearable=False,
                     style={'width': '85px'},
                     className='dbc'),
        dbc.InputGroupText(id=filter_ids.filter_from_date_text,
                           children=season_util
                           .get_season_end_date(season_util.first_played_season())
                           .strftime(date_fmt))

    ],
    className='mb-3',
),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Output(filter_ids.filter_from_date_text, 'children'),
    Input(filter_ids.filter_season_dropdown, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_season_df(season_id, filter_settings):
    if season_id:
        from_date = season_util.get_season_end_date(season_id)

        filter_settings['from_date'] = from_date
        return filter_settings, str(from_date.strftime(date_fmt))
    else:
        return filter_settings, ''


@app.callback(
    Output(filter_ids.filter_season_dropdown, 'options'),
    Output(filter_ids.filter_season_dropdown, 'value'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_season_callback(trigger):
    return season_util.get_season_played(), season_util.first_played_season()
