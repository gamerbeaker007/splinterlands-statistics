import logging
from datetime import datetime

import pandas as pd

from src.configuration import store, config
from src.static.static_values_enum import Edition


def get_card_value(account, list_prices_df, market_prices_df):
    collection_list_value, collection_market_value = get_collection(account, list_prices_df, market_prices_df)
    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account,
                         'collection_market_value': collection_market_value,
                         'collection_list_value': collection_list_value,}, index=[0])


def get_collection(account, list_prices_df, market_prices_df):
    total_list_value = 0
    total_market_value = 0

    for index, collection_card in store.collection.loc[(store.collection.player == account)].iterrows():
        list_flag = False
        market_flag = False
        list_price = 9999999

        list_price_filtered = find_card(collection_card, list_prices_df)
        if not list_price_filtered.empty:
            list_price = float(list_price_filtered.low_price_bcx.iloc[0])
            total_list_value += get_BCX(collection_card) * list_price
            list_flag = True

        market_prices_filtered = find_card(collection_card, market_prices_df)
        if not market_prices_filtered.empty:
            market_price = float(market_prices_filtered.last_bcx_price.iloc[0])
            if list_flag:
                bcx_price = min(market_price, list_price)
            else:
                bcx_price = market_price

            total_market_value += get_BCX(collection_card) * bcx_price
            market_flag = True

        if not list_flag \
                and not market_flag \
                and not collection_card['edition'] == Edition.gladius.value \
                and not collection_card['edition'] == Edition.soulbound.value:
            # TODO in future soulbound may become on the market then warning should be given when not found then

            logging.warning("Card '" +
                            str(collection_card['card_name']) +
                            "' Not found on the markt (list/market) ignore for collection value")

    return int(total_list_value), int(total_market_value)


def find_card(collection_card, market_df):
    mask = (market_df.card_detail_id == collection_card['card_detail_id']) \
           & (market_df.gold == collection_card['gold']) \
           & (market_df.edition == collection_card['edition'])
    filtered_df = market_df.loc[mask]
    return filtered_df


def does_card_match(collection_card, market_card):
    same_id = (collection_card["card_detail_id"] == market_card["card_detail_id"])
    same_foil = (collection_card["gold"] == market_card["gold"])
    same_edition = (collection_card["edition"] == market_card["edition"])
    return same_id and same_foil and same_edition


def get_BCX(collection_card):
    # rarity = self.card_details[int(collection_card["card_detail_id"]) - 1]["rarity"]
    rarity = config.card_details_df.loc[collection_card['card_detail_id']].rarity
    edition = int(collection_card["edition"])
    xp = int(collection_card["xp"])

    if edition == 0:
        if collection_card["gold"]:
            bcx = xp / config.settings["gold_xp"][rarity - 1]
        else:
            bcx = xp / config.settings["alpha_xp"][rarity - 1] + 1
    elif edition == 2 and int(collection_card["card_detail_id"]) > 223:  # all promo cards alpha/beta
        bcx = xp
    elif (edition < 3) or ((edition == 3) and (int(collection_card["card_detail_id"]) <= 223)):
        if collection_card["gold"]:
            bcx = xp / config.settings["beta_gold_xp"][rarity - 1]
        else:
            bcx = xp / config.settings["beta_xp"][rarity - 1] + 1
    else:
        bcx = xp

    return bcx


def get_card_price(card_id, price_list, low_price_string):
    card_price = {}
    for card in price_list:
        if card["card_detail_id"] == card_id:
            if card["edition"] == 0:
                if card["gold"]:
                    card_price["alpha_gold"] = card[low_price_string]
                else:
                    card_price["alpha_regular"] = card[low_price_string]
            elif card["edition"] == 1:
                if card["gold"]:
                    card_price["beta_gold"] = card[low_price_string]
                else:
                    card_price["beta_regular"] = card[low_price_string]

            if card["gold"]:
                card_price["gold"] = card[low_price_string]
            else:
                card_price["regular"] = card[low_price_string]

    return card_price
