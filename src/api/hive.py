import json
from datetime import datetime

import pytz
import requests

url = 'https://api.hive-engine.com/rpc/contracts'
hive_blog_url = 'https://api.hive.blog'


def get_liquidity_positions(account, token_pair):
    query = {"account": account, "tokenPair": token_pair}
    params = {'contract': 'marketpools', 'table': "liquidityPositions", 'query': query}
    j = {'jsonrpc': '2.0', 'id': 1, 'method': 'find', 'params': params}
    with requests.post(url, json=j) as r:
        data = r.json()
        result = data['result']
        if len(result) > 0:
            return float(result[0]['shares'])
        else:
            # no liquidity pool found return 0, 0, 0
            return None


def get_quantity(token_pair):
    query = {"tokenPair": token_pair}
    params = {'contract': 'marketpools', 'table': "pools", 'query': query}
    j = {'jsonrpc': '2.0', 'id': 1, 'method': 'find', 'params': params}
    with requests.post(url, json=j) as r:
        data = r.json()
        result = data['result']
        return float(result[0]['baseQuantity']), \
            float(result[0]['quoteQuantity']), \
            float(result[0]['totalShares'])


def get_hive_transactions(account_name, from_date, till_date, last_id, results):
    limit = 1000
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = '{"jsonrpc":"2.0", ' \
           '"method":"condenser_api.get_account_history", ' \
           '"params":["' + str(account_name) + '" , ' \
           + str(last_id) + ', ' \
           + str(limit) + ', 262144], "id":1}'

    response = requests.post(hive_blog_url, headers=headers, data=data)
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
