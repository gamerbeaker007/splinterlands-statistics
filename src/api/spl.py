import json
import logging
from binascii import hexlify

import pandas as pd
import requests
from beemgraphenebase.ecdsasig import sign_message
from dateutil import parser
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

base_url = 'https://api2.splinterlands.com/'
land_url = 'https://vapi.splinterlands.com/'
prices_url = 'https://prices.splinterlands.com/'

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=['HEAD', 'GET', 'OPTIONS']
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)


def get_card_details():
    address = base_url + 'cards/get_details'
    return pd.DataFrame(http.get(address).json()).set_index('id')


def get_rule_sets_list():
    address = base_url + 'battle/rulesets'
    df = pd.DataFrame(http.get(address).json())
    return df.name.to_list()


def get_player_collection_df(username):
    address = base_url + 'cards/collection/' + username
    collection = http.get(address).json()['cards']
    df = pd.DataFrame(sorted(collection, key=lambda card: card['card_detail_id']))
    return df[['player', 'uid', 'card_detail_id', 'xp', 'gold', 'edition', 'level', 'bcx', 'bcx_unbound']]


def get_battle_history_df(account_name, token_params):
    address = base_url + 'battle/history2'
    params = token_params
    params['player'] = account_name
    params['limit'] = 50
    wild_df = pd.DataFrame()
    wild_result = http.get(address, params=params)
    if wild_result.status_code == 200:
        wild_df = pd.DataFrame(wild_result.json()['battles'])

    params['format'] = 'modern'
    modern_result = http.get(address, params=params)
    modern_df = pd.DataFrame()
    if modern_result.status_code == 200:
        modern_df = pd.DataFrame(modern_result.json()['battles'])

    if wild_df.empty and modern_df.empty:
        return None
    else:
        return pd.concat([wild_df, modern_df])


def get_current_season():
    address = base_url + 'settings'
    current_season = http.get(address).json()['season']

    return current_season


def get_settings():
    address = base_url + 'settings'
    return http.get(address).json()


def is_maintenance_mode():
    return get_settings()['maintenance_mode']


def get_season_end_time(season_id):
    address = base_url + 'season'
    params = {'id': season_id}
    result = http.get(address, params=params)
    if result.status_code == 200:
        date = parser.parse(str(result.json()['ends']))
        result = pd.DataFrame({'id': season_id, 'end_date': str(date)}, index=[0])
    else:
        logging.error('Failed call: '' + str(address) + ''')
        logging.error('Unable to determine season end date return code: ' + str(result.status_code))
        logging.error('This interrupts all other calculations, try re-execution.')
        logging.error('Stopping program now ... ')
        exit(1)
    return result


def get_unclaimed_sps_balance_history_for_token_impl(
        offset=None,
        limit=1000,
        token_params=None):
    balance_history_link = 'players/unclaimed_balance_history'

    params = token_params
    params['token_type'] = 'SPS'
    if offset:
        params['offset'] = offset
    params['limit'] = limit
    address = base_url + balance_history_link

    response = http.get(address, params=params)
    if response.status_code == 200 and response.text != '':
        return response.json()
    else:
        return []


def get_balance_history_for_token_impl_v2(
        token='DEC',
        from_date=None,
        last_update_date=None,
        limit=1000,
        token_params=None):
    token_types = ['SPS', 'DEC', 'VOUCHER', 'CREDITS', 'MERITS', 'GLINT']
    if token not in token_types:
        raise ValueError('Invalid token type. Expected one of: %s' % token_types)

    balance_history_link = 'players/balance_history'

    params = token_params
    params['token_type'] = token
    params['limit'] = limit
    if from_date:
        params["from"] = from_date
    if last_update_date:
        params["last_update_date"] = last_update_date

    response = http.get(base_url + balance_history_link, params=params)
    if response.status_code == 200 and response.text != '':
        return response.json()
    else:
        return None


def player_exist(account_name):
    address = base_url + 'players/details'
    params = {'name': account_name}
    result = http.get(address, params=params)
    if result.status_code == 200 and 'error' not in result.json():
        return True
    else:
        return False


def get_leaderboard_with_player_season(username, season, mode):
    address = base_url + 'players/leaderboard_with_player'
    params = {
        'season': season,
        'format': str(mode.value),
        'username': username
    }

    result = http.get(address, params=params)
    if result.status_code == 200:
        return result.json()['player']
    else:
        return None


def get_deeds_collection(username):
    address = land_url + 'land/deeds'
    params = {
        'status': 'collection',
        'player': username,
    }
    collection = http.get(address, params=params)
    return collection.json()['data']['deeds']


def get_deeds_market():
    address = land_url + 'land/deeds'
    params = {'status': 'market'}
    market = http.get(address, params=params)
    return market.json()['data']['deeds']


def get_balances(username):
    address = base_url + 'players/balances'
    params = {'username': username}
    return http.get(address, params=params).json()


def get_all_cards_for_sale_df():
    address = base_url + 'market/for_sale_grouped'
    all_cards_for_sale = requests.get(address).json()
    return pd.DataFrame(sorted(all_cards_for_sale, key=lambda card: card['card_detail_id']))


def get_tournament(tournament_id):
    address = base_url + 'tournaments/find'
    params = {'id': tournament_id}
    return http.get(address, params=params).json()


def get_player_tournaments_ids(token_params):
    address = base_url + 'players/history'
    params = token_params
    params['from_block'] = -1
    params['limit'] = 500
    params['types'] = 'token_transfer'

    df = pd.DataFrame(http.get(address, params=params).json())
    tournaments_ids = []

    if not df.empty:
        for index, row in df.iterrows():
            data = json.loads(row.data)
            if 'tournament_id' in data:
                tournaments_ids.append(data['tournament_id'])
    return tournaments_ids


def get_market_transaction(trx_id):
    # https://api.splinterlands.io/market/status?id=d8f8593d637ebdd0bca7994dd7e1a15d9f12efa7-0
    address = base_url + 'market/status'
    params = {'id': trx_id}
    result = http.get(address, params=params)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_transaction(trx_id):
    # https://api.splinterlands.com/transactions/lookup?trx_id=247d6ac02bbfd5b8c38528535baa0d8298697a57'
    address = base_url + 'transactions/lookup'
    params = {'trx_id': trx_id}
    result = http.get(address, params=params)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_cards_by_ids(ids):
    # https://api.splinterlands.io/cards/find?ids=C3-457-3VIL75QJ2O,
    address = base_url + 'cards/find'
    params = {'ids': ids}
    result = http.get(address, params=params)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_player_history_season_rewards_df(token_params):
    address = base_url + 'players/history'

    params = token_params
    params['from_block'] = -1
    params['limit'] = 1000
    params['types'] = 'claim_reward'

    result = http.get(address, params=params).json()
    df = pd.DataFrame()
    for row in result:
        df = pd.concat([df, pd.DataFrame(json.loads(row['data']), index=[0])], ignore_index=True)
    if not df.empty:
        df = df.loc[df['type'] == 'league_season']
    return df


def get_battle(battle_id):
    address = base_url + 'battle/result'
    params = {'id': battle_id}
    return http.get(address, params=params).json()


def get_staked_dec_df(account_name):
    address = land_url + 'land/stake/decstaked'
    params = {'player': account_name}
    return pd.DataFrame(http.get(address, params=params).json()['data'])


def compute_sig(string_to_sign: str, private_key: str):
    bytestring_signature = sign_message(string_to_sign, private_key)
    sig = hexlify(bytestring_signature).decode('ascii')
    return sig


def get_token(username, ts, sig):
    login_endpoint = base_url + 'players/v2/login'
    params = {
        'name': username,
        'ts': ts,
        'sig': sig
    }
    result = http.get(login_endpoint, params=params)
    token = ""
    timestamp = ""
    if result and result.status_code == 200:
        result = result.json()
        if 'error' in result:
            raise ValueError(result['error'])

        timestamp = result['timestamp']
        token = result['token']
    return token, timestamp


def verify_token(token_params):
    # Verify token is now done via battle history 2 that needs a specific user token to retrieve data
    if token_params:
        address = base_url + 'battle/history2'
        params = token_params
        result = http.get(address, params=params)
        if result.status_code == 200:
            return True
    return False


def get_owned_resource_sum(account, resource):
    address = land_url + 'land/resources/owned'
    params = {'player': account, 'resource': resource}

    result = http.get(address, params=params).json()
    if result and 'data' in result:
        df = pd.DataFrame(result['data'])
        if 'amount' in df.columns.tolist():
            return df.amount.sum()
    return None


def get_prices():
    address = prices_url + 'prices'
    return http.get(address).json()


def spl_get_pools():
    address = land_url + 'land/liquidity/pools'

    result = http.get(address).json()
    if result and 'data' in result:
        return pd.DataFrame(result['data'])
    return pd.DataFrame()


def get_liquidity(account, resource):
    address = land_url + 'land/liquidity/pools/' + str(account) + '/' + resource

    result = http.get(address).json()
    if result and 'data' in result:
        return pd.DataFrame(result['data']['single'])
    return pd.DataFrame()


def get_land_resources_pools():
    address = land_url + 'land/liquidity/landpools'

    result = http.get(address).json()
    if result and 'data' in result:
        return pd.DataFrame(result['data'])
    return pd.DataFrame()
