import dash_bootstrap_components as dbc
from dash import Output, Input, ctx
from dash.exceptions import PreventUpdate

from src.api import spl
from src.configuration import config
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids
from src.pages.shared_modules import styles
from src.utils import store_util, spl_util
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
    dbc.Row(dbc.Label(id=season_ids.season_update_label, className='text-warning')),
    dbc.Row(dbc.Label(id=season_ids.season_user_update_label, className='text-warning')),
    dbc.Row(dbc.Label(id=season_ids.season_update_token_provided_label, className='text-warning')),
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
    if not store_util.get_token_dict() or store_util.is_last_season_processed(user, current_season_data):
        msg = ''
        display = 'none'
    else:
        display = 'block'
        if spl_util.is_season_reward_claimed(user, current_season_data):
            if config.server_mode:
                msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                      'results are in. Waiting to be process max waiting time: ' + \
                      str(SERVER_MODE_INTERVAL_IN_MINUTES) + ' minutes'
            else:
                msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                      'results are in. Press update seasons to process.'
        else:
            msg = 'Season (' + str(current_season_data['id'] - 1) + ') ' + \
                  'results are NOT processed. Season rewards not claimed yet.'
    return msg, {'display': display}


@app.callback(
    Output(season_ids.season_user_update_label, 'children'),
    Output(season_ids.season_user_update_label, 'style'),
    Input(season_ids.trigger_season_update, 'data'),
)
@measure_duration
def update_season_user_label(tigger):
    msg = ''
    display = 'none'
    for account in store_util.get_account_names():
        if store_util.is_new_account(account):
            # TODO make nice line break comment
            msg = 'One of the accounts is a new account.'
            msg += ' Note it will take from a view minutes for a small account till hours for a large account with many transactions.'
            msg += ' It wil retrieve all battle statistics of all season as well a every balance transaction.'
            msg += ' Transaction from every rental payment/tranfer/claimed sps etc...'
            display = 'block'
            break
    return msg, {'display': display}


@app.callback(
    Output(season_ids.season_update_token_provided_label, 'children'),
    Output(season_ids.season_update_token_provided_label, 'style'),
    Input(season_ids.dropdown_user_selection_season, 'value'),
    Input(season_ids.trigger_season_update, 'data'),
)
@measure_duration
def update_season_token_label(user, tigger):
    if not user:
        raise PreventUpdate

    if store_util.get_token_dict():
        return '', {'display': 'none'}

    return 'Not connected to splinterlands API, update or configure in config page', {'display': 'block'}
