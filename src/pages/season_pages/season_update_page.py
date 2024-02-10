import dash_bootstrap_components as dbc
from dash import Output, Input, ctx, dcc
from dash.exceptions import PreventUpdate

from src.api import spl
from src.configuration import config
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids
from src.pages.shared_modules import styles
from src.utils import store_util
from src.utils.trace_logging import measure_duration
from src.utils.update import SERVER_MODE_INTERVAL_IN_MINUTES

layout = [
    dbc.Row(
        dbc.Col(
            dbc.Button(
                'Update seasons',
                id=season_ids.update_season_btn,
                color='primary',
                n_clicks=0,
                style={'width': '30%'},
                className='mb-3',
            ),
            width='fill',
            style=styles.get_server_mode_style(),
        ),
    ),
    dbc.Row(
        dbc.InputGroup(
            [
                dbc.InputGroupText('Account'),
                dcc.Dropdown(id=season_ids.dropdown_user_selection_season,
                             className='dbc',
                             style={'width': '70%'},
                             ),
            ],
            className='mb-3',
        )
    ),
    dbc.Row(
        dbc.Label(id=season_ids.season_update_label, className='text-warning')
    ),
]


@app.callback(
    Output(season_ids.dropdown_user_selection_season, 'value'),
    Output(season_ids.dropdown_user_selection_season, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(daily_trigger):
    return store_util.get_first_account_name(), store_util.get_account_names()


@app.callback(
    Output(season_ids.trigger_season_update, 'data'),
    Input(season_ids.update_season_btn, 'n_clicks'),
    prevent_initial_call=True,
)
@measure_duration
def update_output(n_clicks):
    if season_ids.update_season_btn == ctx.triggered_id and not config.server_mode:
        store_util.update_data(battle_update=False, season_update=True)
        return True
    return False


@app.callback(
    Output(season_ids.season_update_label, 'children'),
    Output(season_ids.season_update_label, 'style'),
    Input(season_ids.dropdown_user_selection_season, 'value'),
    Input(season_ids.trigger_season_update, 'data'),
)
@measure_duration
def update_season_label(user, tigger):
    if not user:
        raise PreventUpdate

    current_season_data = spl.get_current_season()
    if store_util.is_last_season_processed(user, current_season_data):
        return '', {'display': 'none'}
    else:
        if spl.is_season_reward_claimed(user, current_season_data):
            if config.server_mode:
                msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                      'results are in waiting to be process max waiting time: ' + \
                      str(SERVER_MODE_INTERVAL_IN_MINUTES) + " minutes"
            else:
                msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                      'results are in press update seasons to process'
        else:
            msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                  'results are NOT processed. Season rewards not claimed yet.'

        return msg, {'display': 'block'}
