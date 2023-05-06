import os

import pandas as pd

from src.configuration import configuration
from src.configuration.configuration import Configuration


def write_df(df, file_name, output_type='csv'):
    bas_dir = os.path.join(os.getcwd(), Configuration().store_dir)
    if output_type == 'csv':
        df.to_csv(os.path.join(bas_dir, file_name + ".csv"))
