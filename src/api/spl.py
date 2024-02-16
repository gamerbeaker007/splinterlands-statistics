import json
import logging
from binascii import hexlify
from datetime import datetime
from time import time

import pandas as pd
import requests
from beemgraphenebase.ecdsasig import sign_message
from dateutil import parser
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry
from src.utils import progress_util, store_util

base_url = 'https://api2.splinterlands.com/'
land_url = 'https://vapi.splinterlands.com/'

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


def get_player_collection_df(username):
    address = base_url + 'cards/collection/' + username
    collection = http.get(address).json()['cards']
    df = pd.DataFrame(sorted(collection, key=lambda card: card['card_detail_id']))
    return df[['player', 'uid', 'card_detail_id', 'xp', 'gold', 'edition', 'level']].set_index('uid')


def get_battle_history_df(account_name):
    address = base_url + 'battle/history2?player=' + str(account_name) + store_util.get_token_as_params_string(
        account_name)

    result = http.get(address)
    if result.status_code == 200:
        return pd.DataFrame(result.json()['battles'])
    else:
        return None


def get_current_season():
    address = base_url + 'settings'
    current_season = http.get(address).json()['season']

    return current_season


def get_settings():
    address = base_url + 'settings'
    return http.get(address).json()


def get_season_end_time(season_id):
    address = base_url + 'season?id=' + str(season_id)
    result = http.get(address)
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


def get_balance_history_for_token(username, token='DEC', from_date=None, unclaimed_sps=False):
    limit = 1000
    offset = 0
    max_transactions = 1000000
    print_suffix = ''

    if unclaimed_sps:
        print_suffix = ' UNCLAIMED'

    complete_result = current_result = get_balance_history_for_token_impl(username,
                                                                          token=token,
                                                                          offset=offset,
                                                                          limit=limit,
                                                                          unclaimed_sps=unclaimed_sps)

    while len(current_result) > 0 and offset <= max_transactions:
        progress_util.update_season_msg(str(token) + str(print_suffix) + ' (' + str(username) + ')' +
                                        ': More then \'' + str(offset + limit) +
                                        '\' returned, continue for another balance pull...')
        current_result = get_balance_history_for_token_impl(username,
                                                            token=token,
                                                            offset=offset + limit,
                                                            limit=limit,
                                                            unclaimed_sps=unclaimed_sps)
        complete_result += current_result
        offset += limit
        created_date = parser.parse(complete_result[-1]['created_date'])
        if from_date and from_date > created_date:
            progress_util.update_season_msg(
                token + ': last pull contains all season information data from '' + str(from_date) + '' till NOW')
            break

    if offset > max_transactions:
        progress_util.update_season_msg(
            'Stop pulling data MAX transactions (' + str(max_transactions) + ') reached. Possible not all data pulled')
    progress_util.update_season_msg(token + '(' + str(username) + ')' + ': all data pulled')

    return complete_result


def get_balance_history_for_token_v2(username, token='DEC', start_date=None, unclaimed_sps=False):
    # This tool starts from season x till now. Because it is a history api its backwards
    # So here the end_date is to how far you need to look back. From now till end_date
    end_date = start_date

    limit = 1000
    print_suffix = ''

    if unclaimed_sps:
        print_suffix = ' UNCLAIMED'

    msg_prefix = str(token) + str(print_suffix) + ' (' + str(username) + ') '
    complete_result = []
    from_date = None  # from is none the spl api will make it to current date
    last_update_date = None  # Not needed for the first call

    # Background information from Investygator
    # The reason there's 2 dates is that the "from" (or, created_date in thedata) is essentially the block date,
    # and the last_update_date is when it was actually written to the DB.
    #
    # Since multiple balance updates can happen in the same transaction, sometimes they will have the same "from" date,
    # which can lead to items getting cut off with a limit.
    #
    # The last_update_date should always be distinct, and ensures that you don't get skipped results.
    # However, created_date is the only one indexed, so it's needed for performance reasons.

    while True:
        progress_util.update_season_msg(msg_prefix +
                                        'get balance history (' + str(limit) + ')... ' + str("DATE SOMETHING HERE"))

        data = get_balance_history_for_token_impl_v2(username,
                                                     token=token,
                                                     from_date=from_date,
                                                     last_update_date=last_update_date,
                                                     limit=limit,
                                                     unclaimed_sps=unclaimed_sps)

        if data:
            complete_result += data
            if datetime.strptime(data[-1]["created_date"], "%Y-%m-%dT%H:%M:%S.%fZ") < end_date:
                progress_util.update_season_msg(msg_prefix +
                                                ': last pull contains all season information data from ' +
                                                str(start_date) + ' till NOW')
                break

            # Update the parameters for the next request
            from_date = data[-1]["created_date"]
            last_update_date = data[-1]["last_update_date"]
        else:
            progress_util.update_season_msg(
                msg_prefix + ': last pull contains no data assume all data is collected ' +
                str(start_date) + ' till NOW')
            break

    return complete_result


def get_balance_history_for_token_impl(username, token='DEC', offset=0, limit=1000, unclaimed_sps=False):
    token_types = ['SPS', 'DEC', 'VOUCHER', 'CREDITS', 'MERITS']
    if token not in token_types:
        raise ValueError('Invalid token type. Expected one of: %s' % token_types)

    if unclaimed_sps:
        balance_history_link = 'players/unclaimed_balance_history?token_type='
    else:
        balance_history_link = 'players/balance_history?token_type='

    position_params = '&offset=' + str(offset) + '&limit=' + str(limit)
    address = base_url + balance_history_link + token + position_params + store_util.get_token_as_params_string(
        username)

    response = http.get(address)
    if response.status_code == 200 and response.text != '':
        return response.json()
    else:
        return []


def get_balance_history_for_token_impl_v2(username,
                                          token='DEC',
                                          from_date=None,
                                          last_update_date=None,
                                          limit=1000,
                                          unclaimed_sps=False):
    token_types = ['SPS', 'DEC', 'VOUCHER', 'CREDITS', 'MERITS']
    if token not in token_types:
        raise ValueError('Invalid token type. Expected one of: %s' % token_types)

    if unclaimed_sps:
        balance_history_link = 'players/unclaimed_balance_history'
    else:
        balance_history_link = 'players/balance_history'

    token_param = store_util.get_token(username)
    params = {
        "username": token_param.username,
        'version': token_param.version,
        'token': token_param.token,
        "token_type": token,
        "limit": limit
    }
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
    address = base_url + 'players/details?name=' + str(account_name)
    result = http.get(address)
    if result.status_code == 200 and 'error' not in result.json():
        return True
    else:
        return False


def get_leaderboard_with_player_season(username, season, mode):
    address = base_url + \
              'players/leaderboard_with_player?season=' + str(season) + \
              '&format=' + str(mode.value) + \
              '&username=' + str(username)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()['player']
    else:
        return None


def get_deeds_collection(username):
    address = land_url + 'land/deeds?status=collection&player=' + username
    collection = http.get(address)
    return collection.json()['data']['deeds']


def get_deeds_market():
    address = land_url + 'land/deeds?status=market'
    market = http.get(address)
    return market.json()['data']['deeds']


def get_balances(username):
    address = base_url + 'players/balances?username=' + username
    return http.get(address).json()


def get_all_cards_for_sale_df():
    address = base_url + 'market/for_sale_grouped'
    all_cards_for_sale = requests.get(address).json()
    return pd.DataFrame(sorted(all_cards_for_sale, key=lambda card: card['card_detail_id']))


def get_tournament(tournament_id):
    address = base_url + 'tournaments/find?id=' + str(tournament_id)
    return http.get(address).json()


def get_player_tournaments_ids(username):
    address = base_url + 'players/history?username=' + str(
        username) + '&from_block=-1&limit=500&types=token_transfer'
    result = http.get(address).json()
    tournaments_transfers = list(filter(lambda item: 'enter_tournament' in item['data'], result))
    tournaments_ids = []
    for tournament in tournaments_transfers:
        tournaments_ids.append(json.loads(tournament['data'])['tournament_id'])
    return tournaments_ids


def get_market_transaction(trx_id):
    # https://api.splinterlands.io/market/status?id=d8f8593d637ebdd0bca7994dd7e1a15d9f12efa7-0
    address = base_url + 'market/status?id=' + str(trx_id)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_transaction(trx_id):
    # https://api.splinterlands.com/transactions/lookup?trx_id=247d6ac02bbfd5b8c38528535baa0d8298697a57'
    address = base_url + 'transactions/lookup?trx_id=' + str(trx_id)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_cards_by_ids(ids):
    # https://api.splinterlands.io/cards/find?ids=C3-457-3VIL75QJ2O,
    address = base_url + 'cards/find?ids=' + str(ids)

    result = http.get(address)
    if result.status_code == 200:
        return result.json()
    else:
        return None


def get_player_history_rewards(username):
    address = base_url + 'players/history?username=' + str(
        username) + '&from_block=-1&limit=500&types=card_award,claim_reward'
    return http.get(address).json()


def get_player_history_season_rewards_df(username):
    address = base_url + 'players/history?username=' + str(username) + '&from_block=-1&limit=1000&types=claim_reward'
    result = http.get(address).json()
    df = pd.DataFrame()
    for row in result:
        df = pd.concat([df, pd.DataFrame(json.loads(row['data']), index=[0])], ignore_index=True)
    if not df.empty:
        df = df.loc[df['type'] == 'league_season']
    return df


def get_battle(battle_id):
    address = base_url + 'battle/result?id=' + str(battle_id)
    return http.get(address).json()


def is_maintenance_mode():
    return get_settings()['maintenance_mode']


def is_season_reward_claimed(account, current_season_data):
    df = get_player_history_season_rewards_df(account)
    if df.empty:
        # in this case there are not season rewards found at all assume inactive account or rental account
        # proceed processing balances
        logging.info('No season rewards found at all for account: ' + str(account))
        logging.info('Assume inactive account or rental account continue processing season for : ' + str(account))
        return True

    if df.loc[df.season == current_season_data['id'] - 1].empty:
        logging.info('Season results not claimed yet for account: ' + str(account))
        logging.info('Stop season processing for: ' + str(account))
        return False

    logging.info('Continue season results are claimed for account: ' + str(account))
    return True


def get_staked_dec_df(account_name):
    address = land_url + 'land/stake/decstaked?player=' + str(account_name)
    return pd.DataFrame(http.get(address).json()['data'])


def compute_sig(string_to_sign: str, priv_key: str):
    bytestring_signature = sign_message(string_to_sign, priv_key)
    sig = hexlify(bytestring_signature).decode('ascii')
    return sig


def get_token(username: str, private_key: str):
    login_endpoint = base_url + 'players/v2/login'
    ts = int(time() * 1000)
    sig = compute_sig(username + str(ts), private_key)
    login_endpoint += '?name=' + username + '&ts=' + str(ts) + '&sig=' + sig
    result = http.get(login_endpoint)
    token = ""
    version = ""
    if result and result.status_code == 200:
        result = result.json()
        if 'error' in result:
            raise ValueError(result['error'])

        version = result['timestamp']
        token = result['token']
    return token, version


def verify_token(account_name):
    # Verify token is now done via battle history 2 that needs an specific user token to retrieve data
    token_params = store_util.get_token_as_params_string(account_name)
    if token_params:
        address = base_url + 'battle/history2?' + token_params
        result = http.get(address)
        if result.status_code == 200:
            return True

    return False
