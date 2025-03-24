import logging
from threading import Thread

import pandas as pd

from src.configuration import config, store
from src.pages.main_dash import app
from src.pages.navigation_pages import navigation_page
from src.utils import store_util, update

store_util.load_stores()
store_util.update_season_end_dates()


def migrate_data():
    if (not store.land_resources.empty and
            not store.land_resources.loc[store.land_resources.token_symbol == 'VOUCHER'].empty):
        store.land_resources = store.land_resources[
            store.land_resources.token_symbol != 'VOUCHER'
            ]
    if not 'factor' in store.land_resources.columns:
        df = store.land_resources.copy()
        # Step 1: Create a lookup table for base GRAIN conversion ratios
        conversion_ratios = {
            'WOOD': 4,
            'STONE': 10,
            'IRON': 40
        }

        # Step 3: We'll create a date-to-grain-price map to use in calculations
        grain_prices = df[df['token_symbol'] == 'GRAIN'].set_index('date')['resource_price'].to_dict()

        # Step 4: Filter only rows of interest
        # df_filtered = df[df['token_symbol'].isin(['WOOD', 'STONE', 'IRON'])].copy()

        # Step 5: Calculate grain_equivalent and factor
        def calculate_grain_equivalent_and_factor(row):
            if row['token_symbol'] == 'GRAIN':
                return pd.Series([1, 1])

            grain_price = grain_prices.get(row['date'])
            if grain_price:
                grain_equiv = row['resource_price'] / grain_price
                factor = grain_equiv / conversion_ratios[row['token_symbol']]
                return pd.Series([grain_equiv, factor])
            else:
                return pd.Series([None, None])
        df[['grain_equivalent', 'factor']] = df.apply(calculate_grain_equivalent_and_factor, axis=1)
        store.land_resources = df

    store_util.save_stores()

def main():
    migrate_data()

    if config.server_mode:
        th = Thread(target=update.async_background_task_wrapper)
        th.start()

    app.layout = navigation_page.layout
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', debug=config.debug)


if __name__ == '__main__':
    main()
