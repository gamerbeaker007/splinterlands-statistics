import logging
from datetime import datetime

import pandas as pd

from src.api import spl


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
        listing_price = 0
        df = filter_items(deed, market_df, "deed_type")
        df = filter_items(deed, df, "rarity")
        df = filter_items(deed, df, "plot_status")
        df = filter_items(deed, df, "castle")
        df = filter_items(deed, df, "keep")
        df = filter_items(deed, df, "magic_type")
        if df.empty:
            logging.warning("NO LISTING FOUND FOR DEED: \n"
                            "deed_type: " + str(deed['deed_type']) + "\n" +
                            "rarity: " + str(deed['rarity']) + "\n" +
                            "plot_status: " + str(deed['plot_status']) + "\n" +
                            "castle: " + str(deed['castle']) + "\n" +
                            "keep: " + str(deed['keep']) + "\n" +
                            "magic_type: " + str(deed['magic_type']) + "\n")
            logging.warning("TODO HOW TO DETERMINE PRICE!!!")
        else:
            listing_price = df.astype({'listing_price': 'float'}).listing_price.min()
            deeds_price_found += 1
        deeds_total += listing_price

    return pd.DataFrame({'date': datetime.today().strftime('%Y-%m-%d'),
                         'account_name': account_name,
                         'deeds_qty': deeds_owned,
                         'deeds_price_found_qty': deeds_price_found,
                         'deeds_value': deeds_total}, index=[0])
