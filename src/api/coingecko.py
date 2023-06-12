from pycoingecko import CoinGeckoAPI


def get_current_hive_price():
    cg = CoinGeckoAPI()
    hive_price = cg.get_price(ids='hive', vs_currencies='usd')
    return float(hive_price['hive']['usd'])

