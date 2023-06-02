import requests

url = 'https://api.hive-engine.com/rpc/contracts'


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
            return 0, 0, 0


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

