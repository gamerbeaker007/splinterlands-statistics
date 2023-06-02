from datetime import datetime
from time import sleep

import pandas as pd

from src.api import spl, coingecko, hive
from hiveengine.market import Market


def calculate_value(all_tokens, hive_in_dollar, token, highest_bid):
    if token in all_tokens:
        quantity = all_tokens[token]
        hive_value = float(highest_bid)
        value = hive_value * hive_in_dollar
        return quantity, round(quantity * value, 2)
    else:
        return None, None


def get_all_tokens(account_name):
    all_assets = {}
    for token in spl.get_balances(account_name):
        all_assets[token["token"]] = token["balance"]
    return all_assets


def calculate_prices(df, all_tokens, hive_in_dollar):
    for token in Market():
        if token["symbol"] == "SPS":
            quantity, value = calculate_value(all_tokens, hive_in_dollar, "SPSP", token["highestBid"])
            if quantity:
                df['spsp_qty'] = quantity
                df['spsp_value'] = value
            quantity, value = calculate_value(all_tokens, hive_in_dollar, "SPS", token["highestBid"])
            if quantity:
                df['sps_qty'] = quantity
                df['sps_value'] = value
        elif token["symbol"] == "SLDICE":
            quantity, value = calculate_value(all_tokens, hive_in_dollar, "DICE", token["highestBid"])
            if quantity:
                df['dic_qty'] = quantity
                df['dic_value'] = value
        else:
            this_token = token['symbol']
            quantity, value = calculate_value(all_tokens, hive_in_dollar, this_token, token["highestBid"])
            if quantity:
                df[str(this_token.lower()) + '_qty'] = quantity
                df[str(this_token.lower()) + '_value'] = value
    return df


def get_token_value(account):
    hive_in_dollar = float(coingecko.get_current_hive_price())
    all_tokens = get_all_tokens(account)
    df = pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                       'account_name': account},
                      index=[0])
    df = calculate_prices(df, all_tokens, hive_in_dollar)
    df = get_liquidity_pool(df, account, hive_in_dollar)
    return df


def get_dec_last_price():
    market_list = pd.DataFrame(Market())
    dec_market = market_list.loc[market_list.symbol == 'DEC']
    return float(dec_market.lastPrice.iloc[0])


def get_liquidity_pool(df, account, hive_in_dollar):
    token_pair = "DEC:SPS"
    my_shares = hive.get_liquidity_positions(account, token_pair)
    dec = 0
    sps = 0
    value_usd = 0
    if my_shares:
        dec_qty, sps_qty, total_shares = hive.get_quantity(token_pair)
        share_pct = my_shares / total_shares
        dec = share_pct * dec_qty
        sps = share_pct * sps_qty

        # TODO analyze if sleep is enough else we get an service temporary unavailable
        sleep(1)
        dec_last_price = get_dec_last_price()
        value_hive = dec_last_price * dec
        value_hive = value_hive * 2  # liquidity pool contain equal amount of dec and sps therefor times 2
        value_usd = value_hive * hive_in_dollar
    df['liq_pool_dec_qty'] = dec
    df['liq_pool_sps_qty'] = sps
    df['liq_pool_value'] = value_usd

    return df
