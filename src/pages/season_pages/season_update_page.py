import dash_bootstrap_components as dbc
from dash import Output, Input, ctx, html
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
    dbc.Row(dbc.Label(id=season_ids.season_update_token_provided_label, className='text-warning')),
    dbc.Row(dbc.Label(id=season_ids.season_user_update_label, className='text-warning')),
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
    Input(season_ids.trigger_season_update, 'data'),
)
@measure_duration
def update_season_label(tigger):
    current_season_data = spl.get_current_season()
    season_id = current_season_data['id'] - 1
    not_process_accounts = get_not_process_accounts(season_id)
    if not store_util.get_token_dict() or not not_process_accounts:
        msg = ''
        display = 'none'
    else:
        display = 'block'
        claimed_users, not_claimed_users = get_season_claimed_not_claimed_users(season_id)
        msg = []

        if not_claimed_users:
            msg.append(html.P(
                'Season \'' + str(season_id) + '\' is finished these account(s) have not claimed their rewards:'))
            for user in not_claimed_users:
                msg.append(html.Li(user))
            msg.append(html.P('Claim result on splinterlands website.'))
            msg.append(html.Br())

        if claimed_users:
            msg.append(
                html.P(
                    'Season \'' + str(season_id) + '\' is finished these account(s) have claimed their rewards:'))
            for user in claimed_users:
                if user in not_process_accounts:
                    msg.append(html.Li(user))

            if config.server_mode:
                msg.append(
                    html.P(
                        [
                            'Running in server mode.',
                            html.Br(),
                            'Wait for server to process, wait max: ' + str(
                                SERVER_MODE_INTERVAL_IN_MINUTES) + ' minutes',
                        ]
                    )
                )
                msg.append(html.Br())
            else:
                msg.append(html.P('Click \'Update seasons\' button above to process the results'))
    return msg, {'display': display}


def get_not_process_accounts(season_id):
    not_processed_accounts = []
    for account in store_util.get_account_names():
        if not store_util.is_last_season_processed(account, season_id):
            not_processed_accounts.append(account)

    return not_processed_accounts


def get_season_claimed_not_claimed_users(season_id):
    accounts = store_util.get_account_names()
    not_claimed_users = []
    claimed_users = []
    for account in accounts:
        if spl_util.is_season_reward_claimed(account, season_id):
            claimed_users.append(account)
        else:
            not_claimed_users.append(account)

    return claimed_users, not_claimed_users


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
            msg = [
                'Note:',
                html.Br(),
                'Retrieving data from a new account may take a few minutes for small accounts and several hours ',
                'for large ones with many transactions.',
                html.Br(),
                'The process will gather all seasonal battle stats and every balance transaction,',
                ' including rentals, transfers, and claimed SPS.']
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
