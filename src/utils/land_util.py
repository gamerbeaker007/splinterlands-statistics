import json
import logging
from datetime import datetime

import pandas as pd
from beem.account import Account

from src.api import spl, hive, coingecko


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
    for transaction in transactions:
        info = transaction['trx_info']
        data = json.loads(info['data'])

        if data['op'] == 'harvest_all':
            result = pd.DataFrame(json.loads(info['result'])['result']['data']['results'])
        elif data['op'] == 'harvest_resources':
            result = pd.DataFrame(json.loads(info['result'])['result']['data'], index=[0])
        else:
            logging.error('other land operation: ' + str(data['op']))
            raise Exception('unknown land operation: ' + str(data['op']))

        result['trx_id'] = info['id']
        result['op'] = data['op']
        result['region_uid'] = data['region_uid']
        result['auto_buy_grain'] = data['auto_buy_grain']
        result['created_date'] = info['created_date']
        result['player'] = info['player']
        result['created_date'] = info['created_date']
        results = pd.concat([results, result], ignore_index=True)

    results.reindex(sorted(results.columns), axis=1)
    return results


def get_land_operations(account_name, from_date, till_date):
    acc = Account(account_name)
    land_transactions = hive.get_land_operations(acc, from_date, till_date, -1)
    return process_land_transactions(land_transactions)
