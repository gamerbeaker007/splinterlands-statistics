import logging

import pandas as pd

from src.configuration import store
from src.static.static_values_enum import Edition, Element, CardType, Rarity, ManaCap, MatchType, Format


def get_image_url_markdown(card_name, level, edition):
    base_card_url = 'https://images.hive.blog/100x0/https://d36mxiodymuqjm.cloudfront.net/cards_by_level/'
    edition_name = Edition(edition).name
    markdown_prefix = "![" + str(card_name) + "]"
    card_name = str(card_name).replace(" ", "%20")
    card_url = str(base_card_url) + str(edition_name) + "/" + card_name + "_lv" + str(level) + ".png"
    return str(markdown_prefix) + "(" + str(card_url) + ")"


def get_art_url_markdown(card_name):
    base_card_url = 'https://d36mxiodymuqjm.cloudfront.net/card_art/'
    markdown_prefix = "![" + str(card_name) + "]"
    card_name = str(card_name).replace(" ", "%20")
    card_url = str(base_card_url) + card_name + ".png"
    return str(markdown_prefix) + "(" + str(card_url) + ")"


def get_art_url(card_name):
    base_card_url = 'https://d36mxiodymuqjm.cloudfront.net/card_art/'
    card_name = str(card_name).replace(" ", "%20")
    card_url = str(base_card_url) + card_name + ".png"
    return str(card_url)


def get_image_url(card_name, level, edition):
    base_card_url = 'https://d36mxiodymuqjm.cloudfront.net/cards_by_level/'
    edition_name = Edition(edition).name
    card_name = str(card_name).replace(" ", "%20")
    card_url = str(base_card_url) + str(edition_name) + "/" + card_name + "_lv" + str(level) + ".png"
    return str(card_url)


def get_losing_df(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(store.losing_big, filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        temp_df = temp_df.groupby(['card_detail_id', 'card_name', 'level', 'edition'], as_index=False) \
            .agg(number_of_losses=pd.NamedAgg(column='xp', aggfunc='count'))
        temp_df['url_markdown'] = temp_df.apply(lambda row: get_image_url_markdown(row['card_name'],
                                                                                   row['level'],
                                                                                   row['edition']), axis=1)
        temp_df['url'] = temp_df.apply(lambda row: get_image_url(row['card_name'],
                                                                 row['level'],
                                                                 row['edition']), axis=1)

        temp_df.sort_values('number_of_losses', ascending=False, inplace=True)

    return temp_df


def get_losing_battles_count(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(store.losing_big, filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        return temp_df.battle_id.unique().size
    return 'NA'


def filter_battles(df, filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = df.copy()
    # if ALL filter None :)
    if filter_account == 'ALL':
        filter_account = None
    if filter_type == 'ALL':
        filter_type = None
    if filter_match_type == 'ALL':
        filter_match_type = None

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
    if store.losing_big.empty:
        return store.losing_big
    else:
        temp_df = filter_battles(store.losing_big, filter_account=account, filter_match_type=filter_match_type)
        temp_df = temp_df[['battle_id', 'opponent']]
        temp_df = temp_df.drop_duplicates(subset=['battle_id', 'opponent'])
        temp_df = temp_df.groupby(['opponent'], as_index=False).count()
        temp_df.sort_values('battle_id', ascending=False, inplace=True)
        return temp_df.head(3)


def process_battles_win_percentage(df, group_levels=False):
    if df.empty:
        return df

    group_by_columns = ['card_detail_id',
                        'card_name',
                        'card_type',
                        'rarity',
                        'edition',
                        'color',
                        'secondary_color',
                        'result']
    merge_columns = ['card_detail_id',
                     'card_name',
                     'card_type',
                     'rarity',
                     'edition',
                     'color',
                     'secondary_color']

    if not group_levels:
        group_by_columns.append('level')
        merge_columns.append('level')

    total_df = pd.DataFrame()
    if not df.empty:
        grouped = df.groupby(group_by_columns, as_index=False, dropna=False)
        new_df = grouped.agg(count=pd.NamedAgg(column='account', aggfunc='count'))
        win = new_df.loc[(new_df.result == 'win')].rename(columns={"count": "win", }).drop(['result'], axis=1)
        loss = new_df.loc[(new_df.result == 'loss')].rename(columns={"count": "loss", }).drop(['result'], axis=1)
        total_df = win.merge(loss, on=merge_columns, how='outer')
        total_df = total_df.fillna(0)

        if  group_levels:
            total_df['level'] = total_df.apply(lambda row: df.loc[df.card_detail_id == row.card_detail_id].level.max(), axis=1)

        total_df['win_to_loss_ratio'] = total_df.win / total_df.loss
        total_df['battles'] = total_df.win + total_df.loss
        total_df['win_ratio'] = total_df.win / total_df.battles
        total_df['win_percentage'] = total_df.win_ratio * 100
        total_df = total_df.round(2)

        total_df['url_markdown'] = total_df.apply(lambda row: get_image_url_markdown(row['card_name'],
                                                                                     row['level'],
                                                                                     row['edition']), axis=1)
        total_df['url'] = total_df.apply(lambda row: get_image_url(row['card_name'],
                                                                   row['level'],
                                                                   row['edition']), axis=1)

        total_df.sort_values(['battles', 'win_percentage'], ascending=False, inplace=True)

    return total_df


def filter_element(input_df, filter_settings):
    if input_df.empty:
        return input_df

    list_of_colors = []
    all_true = True
    all_false = True
    for element in Element:
        active = filter_settings[element.name]
        if active:
            all_false = False
            list_of_colors.append(element.value)
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return input_df.loc[(input_df.color.isin(list_of_colors) | input_df.secondary_color.isin(list_of_colors))]


def filter_edition(input_df, filter_settings):
    if input_df.empty:
        return input_df

    list_of_edition_values = []
    all_true = True
    all_false = True
    for edition in Edition:
        active = filter_settings[edition.name]
        if active:
            all_false = False
            list_of_edition_values.append(edition.value)
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return input_df.loc[input_df.edition.isin(list_of_edition_values)]


def filter_card_type(input_df, filter_settings):
    if input_df.empty:
        return input_df

    values = []
    all_true = True
    all_false = True
    for card_type in CardType:
        active = filter_settings[card_type.name]
        if active:
            all_false = False
            values.append(card_type.value)
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return input_df.loc[input_df.card_type.isin(values)]


def filter_rarity(input_df, filter_settings):
    if input_df.empty:
        return input_df

    values = []
    all_true = True
    all_false = True
    for rarity in Rarity:
        active = filter_settings[rarity.name]
        if active:
            all_false = False
            values.append(rarity.value)
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return input_df.loc[input_df.rarity.isin(values)]


def filter_battle_count(input_df, value):
    if input_df.empty:
        return input_df
    return input_df.loc[(input_df.battles >= value)]


def filter_mana_cap(input_df, filter_settings):
    if input_df.empty:
        return input_df

    total_df = pd.DataFrame()
    all_true = True
    all_false = True
    for mana_cap in ManaCap:
        active = filter_settings[mana_cap.name]
        if active:
            all_false = False
            min_value = int(mana_cap.value.split('-')[0])
            max_value = int(mana_cap.value.split('-')[1])

            temp_df = input_df.loc[(input_df.mana_cap >= min_value) & (input_df.mana_cap <= max_value)]
            total_df = pd.concat([total_df, temp_df])
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return total_df


def filter_format(input_df, filter_settings):
    if input_df.empty:
        return input_df

    total_df = pd.DataFrame()
    all_true = True
    all_false = True
    for battle_format in Format:
        active = filter_settings[battle_format.value]
        if active:
            all_false = False

            temp_df = input_df.loc[(input_df.format == battle_format.value)]
            total_df = pd.concat([total_df, temp_df])
        else:
            all_true = False
    if all_true or all_false:
        return input_df
    else:
        return total_df


def filter_date(input_df, filter_settings):
    if input_df.empty:
        return input_df
    from_date = filter_settings['from_date']
    input_df.created_date = pd.to_datetime(input_df.created_date)
    input_df = input_df.loc[input_df.created_date > pd.to_datetime(from_date)]

    return input_df


def filter_rule_sets(input_df, filter_settings):
    rule_sets = filter_settings['rule_sets']
    if input_df.empty or not rule_sets:
        return input_df

    return input_df.loc[(input_df.ruleset1.isin(rule_sets) |
                         input_df.ruleset2.isin(rule_sets) |
                         input_df.ruleset3.isin(rule_sets))]


def sort_by(input_df, sorts):
    if input_df.empty:
        return input_df

    columns = []
    for sort in sorts:
        if sort == 'percentage':
            columns.append('win_percentage')
        else:
            columns.append(sort)
    return input_df.sort_values(columns, ascending=False)


def get_daily_battle_stats(daily_df):
    result_df = pd.DataFrame()
    if not daily_df.empty:
        # Select Ranked battle only
        daily_df = daily_df.loc[(daily_df.match_type == MatchType.RANKED.value)]

        # Select Ranked battles and make dates on day
        daily_df.loc[:, 'created_date'] = pd.to_datetime(daily_df.loc[:, 'created_date']).dt.date

        # First group on battle_id
        daily_df = daily_df.groupby(['battle_id'], as_index=False).agg({'result': 'first',
                                                                        'created_date': 'first',
                                                                        'format': 'first'})
        # second group on day
        win_df = daily_df.loc[daily_df.result == 'win'].groupby(
            ['created_date', 'result', 'format'], as_index=False).agg({'result': 'count'})
        loss_df = daily_df.loc[daily_df.result == 'loss'].groupby(
            ['created_date', 'result', 'format'], as_index=False).agg({'result': 'count'})
        result_df = pd.merge(left=win_df, right=loss_df, on=['created_date', 'format'])
        result_df.rename(columns={"result_x": "win", "result_y": "loss"}, inplace=True)
        result_df['battles'] = result_df.win + result_df.loss
    return result_df


def get_battles_with_used_card(df, card_name):
    result_df = pd.DataFrame()
    if not df.empty:
        battle_ids = df.loc[(df.card_name == card_name)].battle_id.tolist()
        result_df = df.loc[df.battle_id.isin(battle_ids)]

    return result_df


def get_losing_battles(df, battle_ids):
    result_df = pd.DataFrame()
    if not df.empty:
        result_df = df.loc[df.battle_id.isin(battle_ids)]

    return result_df


