import json
import logging

import numpy as np
import pandas as pd
from dateutil import parser

from src.api import hive, spl
from src.configuration import config
from src.static.static_values_enum import Edition
from src.utils import collection_util, progress_util, store_util


def filter_df_last_season(start_date, end_date, data_frame):
    if not data_frame.empty:
        # make sure created_date is of type time date
        date_field = 'created_date'
        data_frame[date_field] = pd.to_datetime(data_frame[date_field])

        # create mask, filter all date between season start and season end date
        mask = (data_frame[date_field] > start_date) & (data_frame[date_field] <= end_date)
        return data_frame.loc[mask].copy()
    return data_frame


def get_last_season_player_history_rewards(account_name, start_date, end_date, season_id):
    player_history_df = pd.DataFrame(spl.get_player_history_rewards(store_util.get_token_dict(account_name)))
    reward_data = pd.DataFrame()

    if not player_history_df.empty:
        # Find season reward
        for index, row in player_history_df.iterrows():
            data = json.loads(row.data)
            if row.success and data['type'] == 'league_season' and data['season'] == season_id:
                reward_data = pd.concat([reward_data, pd.DataFrame(json.loads(row.result)['rewards'])],
                                        ignore_index=True)
                break

        last_season_player_history_rewards = filter_df_last_season(start_date, end_date, player_history_df)

        # Find all quest rewards
        for index, row in last_season_player_history_rewards.iterrows():
            data = json.loads(row.data)
            if row.success and data['type'] == 'quest':
                reward_data = pd.concat([reward_data, pd.DataFrame(json.loads(row.result)['rewards'])],
                                        ignore_index=True)

        # For all reward card subtract addition information
        # TODO empty check beakerr
        reward_data['card_detail_id'] = reward_data.apply(
            lambda r: r.card['card_detail_id'] if r['type'] == 'reward_card' else "", axis=1)
        reward_data['xp'] = reward_data.apply(lambda r: r.card['xp'] if r['type'] == 'reward_card' else "", axis=1)
        reward_data['gold'] = reward_data.apply(lambda r: r.card['gold'] if r['type'] == 'reward_card' else "",
                                                axis=1)

        # Create column if it does not exist (only exists when packs where received)
        if 'edition' not in reward_data:
            reward_data['edition'] = np.nan

        reward_data['edition'] = reward_data.apply(
            lambda r: r.card['edition'] if r['type'] == 'reward_card' else r['edition'], axis=1)
        reward_data['edition_name'] = reward_data.apply(
            lambda r: (Edition(r.edition)).name if r['type'] == 'reward_card' else "", axis=1)
        reward_data['card_name'] = reward_data.apply(
            lambda r: config.card_details_df.loc[r.card_detail_id]['name'] if r['type'] == 'reward_card' else "",
            axis=1)
        reward_data['bcx'] = reward_data.apply(
            lambda r: collection_util.get_bcx(r.card) if r['type'] == 'reward_card' else "", axis=1)

    return reward_data


def get_sold_cards(account_name, cards_df):
    sold_cards = []
    if not cards_df.empty:
        # first remove duplicate card ids
        cards_df = cards_df.drop_duplicates()

        ids = ','.join(cards_df['card'].values.tolist())
        cards = spl.get_cards_by_ids(ids)
        for card in cards:
            if card['player'] != account_name:
                sold_cards += [card]
    return sold_cards


def get_purchased_sold_cards(account_name, start_date, end_date):
    start_date = parser.parse(start_date)
    end_date = parser.parse(end_date)
    transactions = []
    transactions = hive.get_hive_transactions(account_name, start_date, end_date, -1, transactions)

    # filter purchase transactions
    sm_market_purchase = pd.DataFrame()
    potential_sell = pd.DataFrame()
    for transaction in transactions:
        operation = transaction['op'][1]
        if operation['id'] == 'sm_market_purchase':
            df1 = pd.DataFrame({'spl_id': json.loads(operation['json'])['items']})
            sm_market_purchase = pd.concat([sm_market_purchase, df1])
        elif operation['id'] == 'sm_sell_cards':
            card_op = json.loads(operation['json'])
            if isinstance(card_op, dict):
                df1 = pd.DataFrame({'card': card_op['cards']})
                potential_sell = pd.concat([potential_sell, df1])
            else:
                for card in card_op:
                    df1 = pd.DataFrame({'card': card['cards']})
                    potential_sell = pd.concat([potential_sell, df1])

    # process purchases
    purchases = pd.DataFrame()
    if not sm_market_purchase.empty:
        sm_market_purchase = sm_market_purchase.reset_index(drop=True)
        count = sm_market_purchase.count().values[0]
        logging.info("Number card to get: " + str())
        for index, row in sm_market_purchase.iterrows():
            progress_util.update_season_msg("Collecting bought and sold cards transaction: "
                                            + str(index) + "/" + str(count))
            # TODO look into a way to parallel process
            result = spl.get_market_transaction(row.values[0])
            purchases = pd.concat([purchases, pd.DataFrame(result['cards'])])

        purchases['edition_name'] = purchases.apply(lambda r: (Edition(r.edition)).name, axis=1)
        purchases['card_name'] = purchases.apply(lambda r: config.card_details_df.loc[r.card_detail_id]['name'], axis=1)
        purchases['bcx'] = purchases.apply(lambda r: collection_util.get_bcx(r), axis=1)

    sold_cards = pd.DataFrame(get_sold_cards(account_name, potential_sell))
    if not sold_cards.empty:
        sold_cards['edition_name'] = sold_cards.apply(lambda r: (Edition(r.edition)).name, axis=1)
        sold_cards['card_name'] = sold_cards.apply(lambda r: config.card_details_df.loc[r.card_detail_id]['name'],
                                                   axis=1)
        sold_cards['bcx'] = sold_cards.apply(lambda r: collection_util.get_bcx(r), axis=1)

    return purchases, sold_cards
