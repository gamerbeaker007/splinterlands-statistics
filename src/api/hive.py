import json
import logging
from datetime import datetime
from time import sleep

import pytz
import requests
from beem import Hive
from beem.account import Account
from dateutil.parser import isoparse
from hiveengine.api import Api

from src.api import spl, hive_node
from src.utils import progress_util

HIVE_BLOG_URL = 'https://api.hive.blog'

# hive-engine nodes
hive_engine_nodes = [
    'https://api2.hive-engine.com/rpc/',
    'https://api.hive-engine.com/rpc/',
    # 'https://engine.rishipanthee.com/', # is preferred
    'https://herpc.dtools.dev/',
    'https://engine.deathwing.me/',
    'https://ha.herpc.dtools.dev/',
    'https://api.primersion.com/',
    'https://herpc.kanibot.com/',
    'https://he.sourov.dev/',
    'https://herpc.actifit.io/',
    'https://ctpmain.com/',
    'https://he.ausbit.dev/']

max_retries = 1  # This must be inline with the hive_node_list
hive_nodes = [
    'https://api.deathwing.me',
    'https://api.hive.blog',
    # 'https://api.c0ff33a.uk',
    # 'https://rpc.ausbit.dev',
    # 'https://hived.emre.sh',
    # 'https://api.openhive.network',
    # 'https://anyx.io',
    # 'https://techcoderx.com',
    # 'https://hive-api.arcange.eu',
    # 'https://hived.privex.io',
    # 'https://hive.roelandp.nl'
]


def get_liquidity_positions(account, token_pair):
    query = {"account": account, "tokenPair": token_pair}
    result = find_one_with_retry('marketpools', 'liquidityPositions', query)

    if len(result) > 0 and result[0]:
        return float(result[0]['shares'])
    else:
        # no liquidity pool found
        return None


def get_quantity(token_pair):
    query = {"tokenPair": token_pair}
    result = find_one_with_retry('marketpools', 'pools', query)

    return float(result[0]['baseQuantity']), \
        float(result[0]['quoteQuantity']), \
        float(result[0]['totalShares'])


def find_one_with_retry(contract_name, table_name, query):
    result = None
    success = False
    iterations = 3

    #  Might consider special handling when a RPCErrorDoRetry is raised

    # First try with preferred node.
    try:
        api = Api(url=hive_node.PREFERRED_NODE)
        result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
        success = True
    except Exception as e:
        logging.warning('find_one_with_retry (' + type(e).__name__ + ') preferred  node: ' + hive_node.PREFERRED_NODE +
                        '. Continue try on other nodes')
        for iter_ in range(iterations):
            for node in hive_engine_nodes:
                # noinspection PyBroadException
                try:
                    api = Api(url=node)
                    result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
                    success = True
                    hive_node.PREFERRED_NODE = node
                    break
                except Exception as e:
                    logging.warning('find_one_with_retry (' + type(e).__name__ + ') on node: ' + str(
                        node) + '. Continue retry on next node')
                    sleep(1)

            if success:
                break

    if not success:
        raise Exception('find_one_with_retry failed 5 times over all nodes'
                        ' contract:' + str(contract_name) +
                        ' table_name:' + str(table_name) +
                        ' query:' + str(query) +
                        ' stop update .....')
    return result


def get_market_with_retry(token):
    market = find_one_with_retry('market', 'metrics', {'symbol': token})
    if market:
        return market[0]
    else:
        return None


def get_hive_transactions(account_name, from_date, till_date, last_id, results):
    limit = 1000
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = '{"jsonrpc":"2.0", ' \
           '"method":"condenser_api.get_account_history", ' \
           '"params":["' + str(account_name) + '" , ' \
           + str(last_id) + ', ' \
           + str(limit) + ', 262144], "id":1}'

    response = requests.post(HIVE_BLOG_URL, headers=headers, data=data)
    if response.status_code == 200:
        transactions = json.loads(response.text)['result']
        for transaction in transactions:
            timestamp = transaction[1]['timestamp']
            # Assume time of Hive is always UTC
            # https://developers.hive.io/tutorials-recipes/understanding-dynamic-global-properties.html#time
            timestamp = datetime.strptime(timestamp + "-+0000", '%Y-%m-%dT%H:%M:%S-%z')
            if from_date < timestamp < till_date:
                results.append(transaction[1])

        # Check last transaction if there need to be another pull
        timestamp = transactions[0][1]['timestamp']
        timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').astimezone(pytz.utc)
        if from_date < timestamp:
            last_id = transactions[0][0]

            get_hive_transactions(account_name, from_date, till_date, last_id - 1, results)
    return results


def get_rewards_draws(account_name, from_date, till_date, last_id=-1, results=None):
    if results is None:
        results = []

    limit = 100

    history = get_account_history_with_retry(account_name, last_id, limit)
    done = False
    for h in history:
        timestamp = isoparse(h['timestamp'])

        days_to_go = (timestamp - from_date).days
        progress_util.update_season_msg('...retrieve rewards_draws date for \'' + str(account_name) +
                                        '\' - days to go: ' + str(days_to_go))

        last_id = h['index']
        operation = h['id']
        if from_date < timestamp:
            if operation == 'sm_purchase':
                if till_date > timestamp:
                    results.append({'trx_info': spl.get_transaction(h['trx_id'])['trx_info'],
                                    'timestamp': timestamp})
                else:
                    logging.info('Skip.. after till date...')
        else:
            done = True
            break

    if not done:
        get_rewards_draws(account_name, from_date, till_date, last_id - 1, results=results)
    return results


def get_account_history_with_retry(account_name, last_id, limit):
    retries = 0
    while retries < max_retries:
        try:
            account = get_hive_account(account_name, retries)
            history = account.get_account_history(last_id, limit, only_ops=['custom_json'])
            for h in history:
                logging.info("get_account_history success continue....")
                break
            return history
        except Exception as e:
            logging.warning(f"Error occurred: {e}")
            logging.warning("Retrying with a different node...")
            retries += 1
    logging.error("Max retries reached. Unable to fetch account history.")
    return None


def get_land_operations(account_name, from_date, last_id, results=None, days_to_process=None):
    if results is None:
        results = []

    limit = 100

    history = get_account_history_with_retry(account_name, last_id, limit)
    done = False
    for h in history:
        timestamp = isoparse(h['timestamp'])

        if not days_to_process:
            days_to_process = (timestamp - from_date).days + 1

        days_to_go = (timestamp - from_date).days
        pct = (days_to_go / days_to_process * 100 - 100) * -1
        progress_util.update_daily_msg('...retrieve land date for \'' + str(account_name) +
                                       '\' - days to go: ' + str(days_to_go) + ' - ' + str(round(pct)) + '%',
                                       log=False)

        last_id = h['index']
        if from_date < timestamp:
            if h['id'] == 'sm_land_operation':
                results.append({'trx_info': spl.get_transaction(h['trx_id'])['trx_info'],
                                'timestamp': timestamp})
        else:
            done = True
            break

    if not done:
        get_land_operations(account_name, from_date, last_id - 1, results=results, days_to_process=days_to_process)
    return results


def get_hive_account(account_name, retry=0):
    # Now you can use the initialized Hive instance to get account history
    hive = Hive(node=hive_nodes[retry])
    return Account(account_name, hive_instance=hive)
