import pandas as pd
import requests
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

peak_monsters_url = "https://peakmonsters.com/api/market/cards/prices"


def get_market_prices_df():
    return pd.DataFrame(http.get(peak_monsters_url).json()["prices"])
