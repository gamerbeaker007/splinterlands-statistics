import dash_bootstrap_components as dbc
from dash import dcc, Output, Input
from dash.exceptions import PreventUpdate

from main import app
from src import analyse
from src.configuration import store
from src.utils import store_util

load_with_card_id = None
load_with_account_name = None

filter_settings = {'selected-card': '',
                   'account': ''}

layout = dbc.Row([
    dbc.Col(
        dbc.InputGroup(
            [
                dbc.InputGroupText('Account'),
                dcc.Dropdown(store_util.get_account_names(),
                             id='dropdown-user-selection-card-overview',
                             className='dbc',
                             style={'width': '70%'},
                             ),
            ],
            className='mb-3',
        ),
    ),
    dbc.Col(
        dbc.InputGroup(
            [
                dbc.InputGroupText('Played cards'),
                dcc.Dropdown(id='dropdown-card-selection',
                             className='dbc',
                             style={'width': '70%'},
                             ),
            ],
            className='mb-3',
        ),
    ),

]),


@app.callback(Output('dropdown-user-selection-card-overview', 'value'),
              Input('dropdown-user-selection-card-overview', 'state'),
              Input('trigger-daily-update', 'data'),

              )
def update_account_value(state, daily_trigger):
    if load_with_account_name:
        return load_with_account_name
    else:
        return store_util.get_first_account_name()


@app.callback(Output('filtered-cards-df', 'data'),
              Output('filtered-cards-losing-df', 'data'),
              Input('filter-cards-settings', 'data'))
def filter_cards_df(store_filter_settings):
    if store_filter_settings is None or store_filter_settings['account'] == '':
        raise PreventUpdate

    if store_filter_settings['selected-card']:
        # Filter before processing is done
        my_team = analyse.filter_battles(store.battle_big, filter_account=store_filter_settings['account'])
        my_team = analyse.get_battles_with_used_card(my_team, store_filter_settings['selected-card'])
        battle_ids = my_team.battle_id.tolist()

        # Processing
        my_team = analyse.process_battles_win_percentage(my_team, group_by_including_level=False)

        losing_against = analyse.filter_battles(store.losing_big, filter_account=store_filter_settings['account'])
        losing_against = analyse.get_losing_battles(losing_against, battle_ids)

        # Processing
        losing_against['result'] = 'loss'
        losing_against = analyse.process_battles_win_percentage(losing_against, group_by_including_level=False)

        return (my_team.to_json(date_format='iso', orient='split'),
                losing_against.to_json(date_format='iso', orient='split'))
    else:
        return None, None


@app.callback(Output('filter-cards-settings', 'data'),
              Input('dropdown-user-selection-card-overview', 'value'),
              Input('dropdown-card-selection', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def update_filter_settings(account,
                           selected_card,
                           trigger_daily):
    filter_settings['account'] = account
    filter_settings['selected-card'] = selected_card
    return filter_settings


@app.callback(Output('dropdown-card-selection', 'value'),
              Output('dropdown-card-selection', 'options'),
              Input('dropdown-user-selection-card-overview', 'value'),
              Input('trigger-daily-update', 'data'),
              )
def update_card_list(user_selection, tigger):
    if load_with_account_name:
        df = analyse.filter_battles(store.battle_big, filter_account=load_with_account_name)
    else:
        df = analyse.filter_battles(store.battle_big, filter_account=user_selection)

    played_cards = df.card_name.unique().tolist()

    if load_with_card_id:
        value = df.loc[df.card_detail_id == int(load_with_card_id)].card_name.unique().tolist()[0]
    else:
        value = played_cards[0]
    return value, played_cards

