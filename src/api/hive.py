import json
import logging
from datetime import datetime
from time import sleep

import pytz
import requests
from dateutil.parser import isoparse
from hiveengine.api import Api
from hiveengine.rpc import RPCErrorDoRetry

from src.api import spl

PRIMARY_URL = 'https://api2.hive-engine.com/rpc/'
SECONDARY_URL = 'https://api.hive-engine.com/'
HIVE_BLOG_URL = 'https://api.hive.blog'

hive_down_message = "Default hive node 'https://api.hive-engine.com/' down, retry on backup node: " + str(SECONDARY_URL)


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
    # try 10 times on normal API
    for i in range(0, 10):
        # noinspection PyBroadException
        try:
            api = Api(url=PRIMARY_URL)
            result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
            success = True
            break
        except RPCErrorDoRetry:
            sleep(1)
        except Exception as e:
            logging.warning('find_one_with_retry - exception on https://api.hive-engine.com/'
                            ' contract: ' + str(contract_name) +
                            ' table_name: ' + str(table_name) +
                            ' query: ' + str(query) +
                            ' retry on backup url: ' + SECONDARY_URL)
            break

    if not success:
        # try 10 times on backup API
        for i in range(0, 10):
            try:
                # Retry with other hive node
                api = Api(url=SECONDARY_URL)
                result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
                success = True
                break
            except RPCErrorDoRetry:
                logging.warning("find_one_with_retry(10x): backup url try again " + str(i))
                sleep(1)
            except Exception as e:
                logging.warning('find_one_with_retry - fail with backup url rethrow exception')
                raise Exception('find_one_with_retry - fail with backup url rethrow exception'
                                ' contract: ' + str(contract_name) +
                                ' table_name: ' + str(table_name) +
                                ' query: ' + str(query) +
                                ' stop update .....')
    if not success:
        raise Exception('find_one_with_retry failed 20 times.'
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


def get_land_operations(account, from_date, last_id, results=None):
    if results is None:
        results = []

    limit = 100

    history = account.get_account_history(last_id, limit, only_ops=['custom_json'])
    done = False
    for h in history:
        timestamp = isoparse(h['timestamp'])
        last_id = h['index']
        if from_date < timestamp:
            if h['id'] == 'sm_land_operation':
                results.append({'trx_info': spl.get_transaction(h['trx_id'])['trx_info'],
                                'timestamp': timestamp})
        else:
            done = True
            break

    if not done:
        get_land_operations(account, from_date, last_id - 1, results=results)
    return results
