import json
import logging
from datetime import datetime
from time import sleep

import pytz
import requests
from hiveengine.api import Api
from hiveengine.rpc import RPCErrorDoRetry

BACKUP_URL = 'https://api2.hive-engine.com/rpc/'
HIVE_BLOG_URL = 'https://api.hive.blog'

hive_down_message = "Default hive node 'https://api.hive-engine.com/' down, retry on backup node: " + str(BACKUP_URL)


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
        try:
            api = Api()
            result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
            success = True
            break
        except RPCErrorDoRetry:
            sleep(1)

    if not success:
        # try 10 times on backup API
        for i in range(0, 10):
            try:
                # Retry with other hive node
                api = Api(url=BACKUP_URL)
                result = api.find_one(contract_name=contract_name, table_name=table_name, query=query)
                success = True
                break
            except RPCErrorDoRetry:
                logging.warning("find_one_with_retry(10x): backup url try again " + str(i))
                sleep(1)

    if not success:
        raise Exception("find_one_with_retry failed 20 times. " 
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

            get_hive_transactions(account_name, from_date, till_date, last_id-1, results)
    return results
