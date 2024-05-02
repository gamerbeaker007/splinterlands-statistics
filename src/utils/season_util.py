import datetime
import json

import pandas as pd
from beem.account import Account
from dateutil import parser
from dateutil.parser import isoparse

from src import season_balances_info, market_info
from src.api import hive
from src.configuration import store, config
from src.static.static_values_enum import Edition
from src.utils import store_util, progress_util, hive_blog, tournaments_info


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


def generate_season_hive_blog(season_id, users):
    progress_util.set_season_title('Generate hive blog')
    progress_util.update_season_msg('Start collecting last season data')

    season_info_store = {
        'sps': store_util.get_season_values(store.season_sps, season_id, users),
        'dec': store_util.get_season_values(store.season_dec, season_id, users),
        'merits': store_util.get_season_values(store.season_merits, season_id, users),
        'credits': store_util.get_season_values(store.season_credits, season_id, users),
        'vouchers': store_util.get_season_values(store.season_vouchers, season_id, users),
        'glint': store_util.get_season_values(store.season_glint, season_id, users),
        'unclaimed_sps': store_util.get_season_values(store.season_unclaimed_sps, season_id, users),
        'modern_battle': store_util.get_season_values(store.season_modern_battle_info, season_id, users,
                                                      'season'),
        'wild_battle': store_util.get_season_values(store.season_wild_battle_info, season_id, users,
                                                    'season')
    }

    start_date, end_date = season_balances_info.get_start_end_time_season(season_id)
    tournaments_info_dict = {}
    purchases_dict = {}
    sold_dict = {}
    last_season_rewards_dict = {}
    for account_name in users:
        # get tournament information
        progress_util.update_season_msg('Collecting tournament information for: ' + str(account_name))
        tournaments_info_dict[account_name] = tournaments_info.get_tournaments_info(account_name,
                                                                                    start_date,
                                                                                    end_date)

        progress_util.update_season_msg('Collecting bought and sold cards for: ' + str(account_name))
        purchases_dict[account_name], sold_dict[account_name] = market_info.get_purchased_sold_cards(
            account_name,
            start_date,
            end_date)

        # get last season rewards
        progress_util.update_season_msg('Collecting last season reward draws for: ' + str(account_name))
        last_season_rewards_dict[account_name] = get_last_season_reward_draws(
            account_name,
            start_date,
            end_date)
    # print single post for each account
    report = hive_blog.write_blog_post(users,
                                       season_info_store,
                                       last_season_rewards_dict,
                                       tournaments_info_dict,
                                       purchases_dict,
                                       sold_dict,
                                       season_id)
    progress_util.set_season_title('Generate hive blog finished ')
    progress_util.update_season_msg('Done')
    return report


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
        reward_result = json.loads(result['data'])['result']
        if reward_result['success']:
            temp_df = pd.DataFrame(reward_result['rewards'])
            temp_df['type'] = reward_type
            temp_df['sub_type'] = reward_sub_type
            temp_df = temp_df.rename(columns={'quantity': 'bcx'})
            # Expand 'card' column into multiple columns
            card_df = pd.json_normalize(temp_df['card'])
            # Concatenate temp_df and card_df along columns axis
            temp_df = pd.concat([temp_df.drop(columns=['card']), card_df], axis=1)
            df = pd.concat([df, temp_df])

    if not df.empty:
        df['edition_name'] = df.apply(lambda r: (Edition(r.edition)).name, axis=1)
        df['card_name'] = df.apply(lambda r: config.card_details_df.loc[r.card_detail_id]['name'], axis=1)
    return df