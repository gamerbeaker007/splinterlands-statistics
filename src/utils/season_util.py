import datetime
import json

import pandas as pd
from beem.account import Account
from dateutil import parser
from dateutil.parser import isoparse

from src.api import hive
from src.configuration import store, config
from src.static.static_values_enum import Edition
from src.utils import store_util


def get_season_played():
    season_played = store_util.get_seasons_played_list()
    return season_played


def first_played_season():
    season_played = store_util.get_seasons_played_list()
    first_season = ''
    if len(season_played) > 0:
        first_season = season_played[-1]
    return first_season


def get_season_end_date(season_id):
    if season_id != '':
        season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
        from_date = parser.parse(season_end_date)
        return from_date
    return datetime.date(2018, 5, 26)  # start of splinterlands


def get_last_season_reward_draws(account_name, from_date, till_date):
    from_date = isoparse(from_date).replace(tzinfo=None)
    till_date = isoparse(till_date).replace(tzinfo=None)
    acc = Account(account_name)

    results = hive.get_rewards_draws(acc, from_date, till_date)

    df = pd.DataFrame()
    for result in results:
        result = json.loads(result['trx_info']['result'])
        reward_type = result['type']
        reward_sub_type = result['sub_type']
        bcx = result['quantity']
        reward_result = json.loads(result['data'])['result']
        if reward_result['success']:
            temp_df = pd.DataFrame(reward_result['rewards'])
            temp_df['type'] = reward_type
            temp_df['sub_type'] = reward_sub_type
            temp_df['bcx'] = bcx
            # Expand 'card' column into multiple columns
            card_df = pd.json_normalize(temp_df['card'])
            # Concatenate temp_df and card_df along columns axis
            temp_df = pd.concat([temp_df.drop(columns=['card']), card_df], axis=1)
            df = pd.concat([df, temp_df])

    if not df.empty:
        df['edition_name'] = df.apply(lambda r: (Edition(r.edition)).name, axis=1)
        df['card_name'] = df.apply(lambda r: config.card_details_df.loc[r.card_detail_id]['name'], axis=1)

    return df
