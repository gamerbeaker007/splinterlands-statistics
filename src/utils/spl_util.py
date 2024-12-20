import logging

import pandas as pd
from dateutil import parser
from dateutil.parser import isoparse
from pandas import json_normalize

from src.api import spl
from src.utils import progress_util, store_util


def get_unclaimed_sps_balance_history_for_token(username, start_date=None):
    limit = 1000
    offset = None

    msg_prefix = 'SPS UNCLAIMED (' + str(username) + ') '
    token_params = store_util.get_token_dict(username)

    total_items = 0
    complete_result = []
    while True:

        data = spl.get_unclaimed_sps_balance_history_for_token_impl(
            offset=offset,
            limit=limit,
            token_params=token_params
        )

        if data:
            print('sps_unclaimed: ' + str(data[-1]['created_date']))
            complete_result += data
            offset = data[-1]["id"]
            total_items += len(data)
            progress_util.update_season_msg(
                msg_prefix +
                ' get unclaimed sps balance history total found items: ' +
                str(total_items))

            created_date = parser.parse(complete_result[-1]['created_date'])
            if start_date and created_date < start_date:
                progress_util.update_season_msg(
                    msg_prefix +
                    ' last pull contains all season information data from ' +
                    str(start_date) + ' till NOW')
                break
        else:
            progress_util.update_season_msg(
                msg_prefix +
                ': last pull contains no data assume all data is collected ' +
                str(start_date) + ' till NOW')
            break
    progress_util.update_season_msg(msg_prefix + ': all data pulled')
    return complete_result


def get_balance_history_for_token(username, token='DEC', start_date=None):
    limit = 1000

    token_params = store_util.get_token_dict(username)

    msg_prefix = str(token) + ' (' + str(username) + ') '
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
        data = spl.get_balance_history_for_token_impl_v2(
            token=token,
            from_date=from_date,
            last_update_date=last_update_date,
            limit=limit,
            token_params=token_params
        )

        if data:
            update_message(data, msg_prefix)

            complete_result += data
            # Update the parameters for the next request
            from_date = data[-1]["created_date"]
            last_update_date = data[-1]["last_update_date"]

            if start_date and parser.parse(from_date) < start_date:
                progress_util.update_season_msg(
                    msg_prefix +
                    ': last pull contains all season information data from ' +
                    str(start_date) + ' till NOW')
                break

        else:
            progress_util.update_season_msg(
                msg_prefix +
                ': last pull contains no data assume all data is collected ' +
                str(start_date) + ' till NOW')
            break

    return complete_result


def update_message(data, msg_prefix):
    date_str = data[-1]['created_date']
    date_obj = isoparse(date_str)
    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')

    progress_util.update_season_msg(
        msg_prefix + 'get balance history: ' +
        str(formatted_date)
    )


def get_battle_history_df(account):
    return spl.get_battle_history_df(account, store_util.get_token_dict(account))


def is_season_reward_claimed(account, season_id):
    df = spl.get_player_history_season_rewards_df(store_util.get_token_dict(account))
    if df.empty:
        # in this case there are not season rewards found at all assume inactive account or rental account
        # proceed processing balances
        logging.info('No season rewards found at all for account: ' + str(account))
        logging.info('Assume inactive account or rental account continue processing season for : ' + str(account))
        return True

    if df.loc[df.season == season_id].empty:
        logging.info('Season results not claimed yet for account: ' + str(account))
        logging.info('Stop season processing for: ' + str(account))
        return False

    logging.info('Continue season results are claimed for account: ' + str(account))
    return True


def get_ability_list():
    cards = spl.get_card_details()
    abilities_df = json_normalize(cards['stats']).abilities.dropna()
    flattened_abilities = [ability for sublist in abilities_df for ability in sublist if sublist]

    unique_abilities = {ability for sublist in flattened_abilities for ability in
                        (sublist if isinstance(sublist, list) else [sublist])}

    series = pd.Series(list(unique_abilities))
    return series.sort_values()
