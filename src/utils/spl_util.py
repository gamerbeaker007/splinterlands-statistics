import logging

from dateutil import parser

from src.api import spl
from src.configuration import config
from src.utils import progress_util, store_util


def get_balance_history_for_token(username, token='DEC', from_date=None, unclaimed_sps=False):
    limit = 1000
    offset = 0
    max_transactions = 1000000
    print_suffix = ''

    if unclaimed_sps:
        print_suffix = ' UNCLAIMED'

    token_params = store_util.get_token_dict(username)

    complete_result = current_result = spl.get_balance_history_for_token_impl(
        token=token,
        offset=offset,
        limit=limit,
        unclaimed_sps=unclaimed_sps,
        token_params=token_params
    )

    while len(current_result) > 0 and offset <= max_transactions:
        progress_util.update_season_msg(str(token) + str(print_suffix) + ' (' + str(username) + ')' +
                                        ': More then \'' + str(offset + limit) +
                                        '\' returned, continue for another balance pull...')
        current_result = spl.get_balance_history_for_token_impl(
            token=token,
            offset=offset + limit,
            limit=limit,
            unclaimed_sps=unclaimed_sps,
            token_params=token_params
        )
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
    limit = 1000

    print_suffix = ''
    if unclaimed_sps:
        print_suffix = ' UNCLAIMED'

    token_params = store_util.get_token_dict(username)

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
        data = spl.get_balance_history_for_token_impl_v2(
            token=token,
            from_date=from_date,
            last_update_date=last_update_date,
            limit=limit,
            unclaimed_sps=unclaimed_sps,
            token_params=token_params
        )

        progress_util.update_season_msg(
            msg_prefix +
            'get balance history found items: ' +
            str(len(data))
        )

        if data:
            complete_result += data
            # Update the parameters for the next request
            from_date = data[-1]["created_date"]
            last_update_date = data[-1]["last_update_date"]

            if parser.parse(from_date) < parser.parse(start_date):
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


def get_battle_history_df(account):
    return spl.get_battle_history_df(account, store_util.get_token_dict(account))


def is_season_reward_claimed(account, current_season_data):
    df = spl.get_player_history_season_rewards_df(account)
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


def get_rule_sets_list():
    rule_sets = config.settings['battles']['rulesets']
    list_of_ruleset = []
    for rule_set in rule_sets:
        list_of_ruleset.append(rule_set['name'])
    return list(list_of_ruleset)
