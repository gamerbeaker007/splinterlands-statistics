
import requests
from requests.adapters import HTTPAdapter
from src.api.logRetry import LogRetry

base_url_api2 = "https://api2.splinterlands.com/"

retry_strategy = LogRetry(
    total=10,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

def get_card_details():
    address = base_url_api2 + "cards/get_details"
    return http.get(address).json()


