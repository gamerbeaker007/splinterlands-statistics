import logging

import pandas as pd
import requests
from dateutil import parser
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

base_url = "https://api2.splinterlands.com/"

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


def get_card_details():
    address = base_url + "cards/get_details"
    return pd.DataFrame(http.get(address).json()).set_index('id')


def get_player_collection_df(username):
    address = base_url + "cards/collection/" + username
    collection = http.get(address).json()["cards"]
    df = pd.DataFrame(sorted(collection, key=lambda card: card["card_detail_id"]))
    return df[['player', 'uid', 'card_detail_id', 'xp', 'gold', 'edition', 'level']].set_index('uid')


def get_battle_history_df(account_name):
    address = base_url + "battle/history?player=" + str(account_name)

    result = http.get(address)
    if result.status_code == 200:
        return pd.DataFrame(result.json()['battles'])
    else:
        return None


def get_current_season():
    address = base_url + "settings"
    current_season = http.get(address).json()['season']

    return current_season


def get_season_end_times():
    season = get_current_season()
    till_season_id = season['id']
    logging.info("Retrieve season end dates for '" + str(till_season_id) + "' seasons")
    # https://api.splinterlands.com/season?id=1
    season_end_dates_array = []

    for season in range(1, till_season_id + 1):
        address = base_url + "season?id=" + str(season)
        result = http.get(address)
        if result.status_code == 200:
            date = parser.parse(str(result.json()['ends']))
            season_end_dates_array.append({'id': season, 'date': date})
        else:
            logging.error("Failed call: '" + str(address) + "'")
            logging.error("Unable to determine season end date return code: " + str(result.status_code))
            logging.error("This interrupts all other calculations, try re-execution.")
            logging.error("Stopping program now ... ")
            exit(1)

    return season_end_dates_array


def get_balance_history_for_token(username, token="DEC", from_date=None, unclaimed_sps=False):
    limit = 1000
    offset = 0
    max_transactions = 1000000
    print_suffix = ""

    if unclaimed_sps:
        print_suffix = " UNCLAIMED"

    complete_result = current_result = get_balance_history_for_token_impl(username,
                                                                          token=token,
                                                                          offset=offset,
                                                                          limit=limit,
                                                                          unclaimed_sps=unclaimed_sps)

    while len(current_result) > 0 and offset <= max_transactions:
        logging.info(str(token) + str(print_suffix) + " (" + str(username) + ")" +
                     ": More then '" + str(offset + limit) +
                     "' returned, continue for another balance pull...")
        current_result = get_balance_history_for_token_impl(username,
                                                            token=token,
                                                            offset=offset + limit,
                                                            limit=limit,
                                                            unclaimed_sps=unclaimed_sps)
        complete_result += current_result
        offset += limit
        created_date = parser.parse(complete_result[-1]['created_date'])
        if from_date and from_date > created_date:
            logging.info(
                token + ": last pull contains all season information data from '" + str(from_date) + "' till NOW")
            break

    if offset > max_transactions:
        logging.info(
            "Stop pulling data MAX transactions (" + str(max_transactions) + ") reached. Possible not all data pulled")
    logging.info(token + "(" + str(username) + ")" + ": all data pulled")

    return complete_result


def get_balance_history_for_token_impl(username, token="DEC", offset=0, limit=1000, unclaimed_sps=False):
    token_types = ["SPS", "DEC", "VOUCHER", "CREDITS", "MERITS"]
    if token not in token_types:
        raise ValueError("Invalid token type. Expected one of: %s" % token_types)

    if unclaimed_sps:
        balance_history_link = "players/unclaimed_balance_history?token_type="
    else:
        balance_history_link = "players/balance_history?token_type="
    address = base_url + str(balance_history_link) + str(token) + "&username=" + str(
        username) + "&offset=" + str(offset) + "&limit=" + str(limit)

    response = http.get(address)
    if response.status_code == 200 and response.text != '':
        return response.json()
    else:
        return []


def player_exist(account_name):
    address = base_url + "players/details?name=" + str(account_name)
    result = http.get(address)
    if result.status_code == 200 and 'error' not in result.json():
        return True
    else:
        return False
