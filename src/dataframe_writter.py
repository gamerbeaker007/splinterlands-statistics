import os

from src.configuration import config


def write_df(df, file_name, output_type='csv'):
    bas_dir = os.path.join(os.getcwd(), config.store_dir)
    if output_type == 'csv':
        df.to_csv(os.path.join(bas_dir, file_name + ".csv"))
