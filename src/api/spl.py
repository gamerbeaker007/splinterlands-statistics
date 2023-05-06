import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from src.api.logRetry import LogRetry

base_url = "https://api2.splinterlands.com/"

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)


def get_card_details():
    address = base_url + "cards/get_details"
    return http.get(address).json()


def get_player_collection_df(username):
    address = base_url + "cards/collection/" + username
    collection = http.get(address).json()["cards"]
    df = pd.DataFrame(sorted(collection, key=lambda card: card["card_detail_id"]))
    return df[['player', 'uid', 'card_detail_id', 'xp', 'gold', 'edition', 'level']].set_index('uid')
