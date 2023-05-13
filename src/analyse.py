import logging

from src.configuration import store, config


def get_losing_df(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        temp_df = temp_df.groupby(['card_detail_id', 'level', ], as_index=False).count()
        # Keep columns
        temp_df = temp_df[['card_detail_id', 'level', 'xp']]
        temp_df.rename(columns={'xp': 'number_of_losses'}, inplace=True)
        temp_df['name'] = temp_df.apply(
            lambda row: (config.card_details_df.loc[row.card_detail_id]['name']), axis=1)

        temp_df.sort_values('number_of_losses', ascending=False, inplace=True)
    return temp_df


def get_battles_df(filter_account=None, filter_match_type=None, filter_type=None):
    temp_df = filter_battles(filter_account, filter_match_type, filter_type)
    if not temp_df.empty:
        return temp_df.battle_id.unique().size
    return 'NA'


def filter_battles(filter_account=None, filter_match_type=None, filter_type=None):
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


def get_top_3_losing_account(account):
    temp_df = store.losing_big_df.copy()
    temp_df = temp_df.loc[(temp_df.account == account)][['battle_id', 'opponent']]
    temp_df = temp_df.drop_duplicates(subset=['battle_id', 'opponent'])
    temp_df = temp_df.groupby(['opponent'], as_index=False).count()
    temp_df.sort_values('opponent', inplace=True)

    return temp_df.head(3)
