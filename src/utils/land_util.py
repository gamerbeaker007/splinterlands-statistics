import json
import logging
from datetime import datetime

import pandas as pd

from src.api import spl, hive, coingecko
from src.static.static_values_enum import LAND_SWAP_FEE
from src.utils import progress_util


def filter_items(deed, df, param):
    if deed[param]:
        # return matching values
        return df.loc[(df[param] == deed[param])]
    else:
        # return value either None or ""
        return df[(df[param].isnull()) | (df[param] == "")]


def get_deeds_value(account_name):
    collection = spl.get_deeds_collection(account_name)
    market_df = pd.DataFrame(spl.get_deeds_market())
    deeds_price_found = 0
    deeds_owned = 0
    deeds_total = 0.0
    for deed in collection:
        deeds_owned += 1
        filter_types = ["rarity", 'plot_status', 'magic_type', 'deed_type']
        df = market_df
        missing_types = []
        for filter_type in filter_types:
            temp = filter_items(deed, df, filter_type)
            if not temp.empty:
                df = temp
            else:
                missing_types.append(filter_type)
        if missing_types:
            logging.warning("Not a perfect match found missing filters: " + str(missing_types))
            logging.warning("Was looking for: \n" +
                            "\n".join([str(x) + ": " + str(deed[x]) for x in filter_types]))
            logging.warning("Current estimated best value now: " +
                            str(df.astype({'listing_price': 'float'}).listing_price.min()))
        listing_price = df.astype({'listing_price': 'float'}).listing_price.min()
        deeds_price_found += 1

        deeds_total += listing_price

    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account_name,
                         'deeds_qty': deeds_owned,
                         'deeds_price_found_qty': deeds_price_found,
                         'deeds_value': deeds_total}, index=[0])


def get_staked_dec_value(account_name):
    dec_staked_value = 0
    dec_staked_qty = 0

    dec_staked_df = spl.get_staked_dec_df(account_name)
    if not dec_staked_df.empty:
        dec_staked_qty = dec_staked_df.amount.sum()
        token_market = hive.get_market_with_retry('DEC')
        hive_in_dollar = float(coingecko.get_current_hive_price())

        if token_market:
            hive_value = float(token_market["highestBid"])
            dec_staked_value = round(hive_value * hive_in_dollar * dec_staked_qty, 2)

    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account_name,
                         'dec_staked_qty': dec_staked_qty,
                         'dec_staked_value': dec_staked_value}, index=[0])


def process_land_transactions(transactions):
    results = pd.DataFrame()
    if transactions:
        for transaction in transactions:
            info = transaction['trx_info']
            data = json.loads(info['data'])

            process = True
            if data['op'] == 'harvest_all':
                temp = json.loads(info['result'])['result']
                if temp['success']:
                    result = pd.DataFrame(temp['data']['results'])
                else:
                    logging.info('Ignore false transaction...: ' + str(data['op']))
                    process = False
            elif data['op'] in ['harvest_resources', 'mine_sps', 'mine_research']:
                temp = json.loads(info['result'])['result']
                if temp['success']:
                    result = pd.DataFrame(temp['data'], index=[0])
                else:
                    logging.info('Ignore false transaction...: ' + str(data['op']))
                    process = False
            elif data['op'] == 'tax_collection':
                temp = json.loads(info['result'])['result']
                if temp['success']:
                    result = pd.DataFrame(temp['data'])
                    for token in result.tokens.values[0]:
                        result[token['token'] + '_received_tax'] = token['received']
                    result.drop('tokens', axis=1, inplace=True)
                else:
                    logging.info('Ignore false transaction...: ' + str(data['op']))
                    process = False
            else:
                logging.info('Ignore land operation: ' + str(data['op']))
                process = False

            if process:
                result['trx_id'] = info['id']
                result['op'] = data['op']
                result['region_uid'] = data['region_uid']
                result['auto_buy_grain'] = data['auto_buy_grain']
                result['created_date'] = info['created_date']
                result['player'] = info['player']
                result['created_date'] = info['created_date']  # spl created date
                result['timestamp'] = transaction['timestamp']  # timestamp hive transaction

                results = pd.concat([results, result], ignore_index=True)

        results = results.reindex(sorted(results.columns), axis=1)
    return results


def get_land_operations(account_name, from_date):
    progress_util.update_daily_msg('...retrieve land data for \'' + str(account_name) + '\'')

    now = datetime.now()
    land_transactions = hive.get_spl_transactions(account_name, from_date, till_date=now,
                                                  filter_spl_transactions=['sm_land_operation'])

    progress_util.update_daily_msg('...processing land data for \'' + str(account_name) + '\'')

    return process_land_transactions(land_transactions)


def get_resources_value(account):
    dec_value = spl.get_prices()['dec']
    pools = spl.spl_get_pools()
    total_value = 0
    if not pools.empty:
        for resource in pools.token_symbol.tolist():
            pool = pools.loc[pools.token_symbol == resource].iloc[0]
            qty = spl.get_owned_resource_sum(account, resource)
            if qty:
                value_dec = qty * pool.resource_price * LAND_SWAP_FEE
                total_value += value_dec * dec_value

    return pd.DataFrame({'date': [datetime.today().strftime('%Y-%m-%d')],
                         'account_name': [account],
                         'land_resources_value': [total_value]})


def get_liquidity_pools_info(account):
    pools = spl.spl_get_pools()

    date = datetime.today().strftime('%Y-%m-%d')

    dec_value = spl.get_prices()['dec']

    if not pools.empty:
        for resource in pools.token_symbol.tolist():
            pool = pools.loc[pools.token_symbol == resource].iloc[0]
            liq = spl.get_liquidity(account, resource)
            token = 'DEC-' + resource
            if not liq.empty and not liq.loc[liq.token == token].empty:
                liq = liq.loc[liq.token == token].iloc[0]
                my_shares = liq.balance
                total_shares = float(pool.total_shares)
                my_pct = (my_shares / total_shares) * 100
                resource_qty = float(pool.resource_quantity) / 100 * my_pct
                dec_qty = float(pool.dec_quantity) / 100 * my_pct

                return pd.DataFrame({
                    'date': [date],
                    'account_name': [account],
                    'token': [token],
                    'my_shares': [my_shares],
                    'my_pct': [my_pct],
                    'my_resource_quantity': [resource_qty],
                    'my_dec_quantity': [dec_qty],
                    'value': [dec_qty * dec_value * 2],
                    'total_shares': float(pool.resource_quantity),
                    'resource_quantity': float(pool.resource_quantity),
                    'dec_quantity': float(pool.dec_quantity),
                    'resource_price': [float(pool.resource_price)],
                    'dec_price': [float(pool.dec_price)],
                    'dec_price_usd': [dec_value],
                })

    return pd.DataFrame()
