import logging
from time import sleep

from beem import Hive
from beem.account import Account
from dateutil.parser import isoparse
from hiveengine.api import Api

from src.api import spl, hive_node
from src.utils import progress_util

HIVE_BLOG_URL = 'https://api.hive.blog'

# hive-engine nodes see https://beacon.peakd.com/
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

# hive nodes see https://beacon.peakd.com/
hive_nodes = [
    'https://api.deathwing.me',
    'https://api.hive.blog',
    'https://hive-api.arcange.eu',
    'https://api.openhive.network'
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


def get_spl_transactions(account_name,
                         from_date,
                         till_date,
                         last_id=-1,
                         filter_spl_transactions=None,
                         results=None):
    if filter_spl_transactions is None:
        filter_spl_transactions = ['sm_purchase', 'sm_market_purchase', 'sm_sell_cards', 'sm_claim_reward']

    if results is None:
        results = []

    history = get_account_history_with_retry(account_name, last_id)
    if history:
        done = False
        for h in history:
            timestamp = isoparse(h['timestamp'])

            days_to_go = (timestamp - from_date).days
            progress_util.update_season_msg('...retrieve hive transaction for \'' + str(account_name) +
                                            '\' - days to go: ' + str(days_to_go))

            last_id = h['index']
            operation = h['id']
            if from_date < timestamp:
                if operation in filter_spl_transactions:
                    if till_date > timestamp:
                        results.append({'trx_info': spl.get_transaction(h['trx_id'])['trx_info'],
                                        'operation': h['id'],
                                        'timestamp': timestamp})
                    else:
                        logging.info('Skip.. after till date...')
            else:
                done = True
                break

        if not done:
            get_spl_transactions(account_name,
                                 from_date,
                                 till_date,
                                 last_id=last_id - 1,
                                 filter_spl_transactions=filter_spl_transactions,
                                 results=results)
    return results


def get_account_history_with_retry(account_name, last_id):
    limit = 100
    retries = 0
    while retries < len(hive_nodes):
        try:
            account = get_hive_account(account_name, retries)
            history = account.get_account_history(last_id, limit, only_ops=['custom_json'])
            success = False
            return_list = []
            for h in history:
                success = True
                return_list.append(h)

            if success:
                logging.info("get_account_history success continue....")
                return return_list

            logging.warning("Retrying with a different hive node...")
            retries += 1
        except Exception as e:
            logging.warning(f"Error occurred: {e}")
            logging.warning("Retrying with a different hive node...")
            retries += 1
    logging.error("Max retries reached. Unable to fetch account history.")
    return None


def get_hive_account(account_name, retry=0):
    # Now you can use the initialized Hive instance to get account history
    hive = Hive(node=hive_nodes[retry])
    return Account(account_name, hive_instance=hive)
