import logging

import pandas as pd

from src.configuration import store
from src.static.static_values_enum import Edition


def get_image_url_markdown(card_name, level, edition):
    base_card_url = 'https://images.hive.blog/100x0/https://d36mxiodymuqjm.cloudfront.net/cards_by_level/'
    edition_name = Edition(edition).name
    markdown_prefix = "![" + str(card_name) + "]"
    card_name = str(card_name).replace(" ", "%20")
    card_url = str(base_card_url) + str(edition_name) + "/" + card_name + "_lv" + str(level) + ".png"
    return str(markdown_prefix) + "(" + str(card_url) + ")"


def get_losing_df(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        temp_df = temp_df.groupby(['card_detail_id', 'card_name', 'level', 'edition'], as_index=False)\
            .agg(number_of_losses=pd.NamedAgg(column='xp', aggfunc='count'))
        temp_df['url'] = temp_df.apply(lambda row: get_image_url_markdown(row['card_name'],
                                                                          row['level'],
                                                                          row['edition']), axis=1)

        temp_df.sort_values('number_of_losses', ascending=False, inplace=True)

    return temp_df


def get_battles_df(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        return temp_df.battle_id.unique().size
    return 'NA'


def filter_battles(filter_account=None, filter_match_type=None, filter_type=None):
    # if ALL filter None :)
    if filter_account == 'ALL':
        filter_account = None
    if filter_type == 'ALL':
        filter_type = None
    if filter_match_type == 'ALL':
        filter_match_type = None

    temp_df = store.losing_big_df.copy()
    if not temp_df.empty:
        if filter_account:
            temp_df = temp_df.loc[(temp_df.account == filter_account)]

        if filter_match_type:
            temp_df = temp_df.loc[(temp_df.match_type == filter_match_type)]

        if filter_type:
            temp_df = temp_df.loc[(temp_df.card_type == filter_type)]
    else:
        logging.info('No battles found at all')
    return temp_df


def get_top_3_losing_account(account, filter_match_type):
    temp_df = filter_battles(filter_account=account, filter_match_type=filter_match_type)
    temp_df = temp_df[['battle_id', 'opponent']]
    temp_df = temp_df.drop_duplicates(subset=['battle_id', 'opponent'])
    temp_df = temp_df.groupby(['opponent'], as_index=False).count()
    temp_df.sort_values('battle_id', ascending=False, inplace=True)

    return temp_df.head(3)
