import logging

from src.configuration import store, config


def print_top_ten_losing(match_type=None):
    temp_df = store.losing_big_df.copy()
    if match_type:
        temp_df = temp_df.loc[(temp_df.match_type == match_type.value)]

    if not temp_df.empty:
        temp_df = temp_df.groupby(['card_detail_id', 'level'], as_index=False).count()[['card_detail_id', 'level', 'xp']]
        temp_df.rename(columns={'xp': 'number_of_losses'}, inplace=True)
        temp_df['name'] = temp_df.apply(
            lambda row: (config.card_details_df.loc[row.card_detail_id]['name']), axis=1)
        temp_df['type'] = temp_df.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['type'], axis=1)

        summoners_df = temp_df.loc[(temp_df.type == 'Summoner')].copy()
        summoners_df.sort_values('number_of_losses', ascending=False, inplace=True)
        monsters_df = temp_df.loc[(temp_df.type == 'Monster')].copy()
        monsters_df.sort_values('number_of_losses', ascending=False, inplace=True)

        suffix = ': '
        if match_type:
            suffix = ' ' + str(match_type) + ': '
        logging.info('Top ten losing cards' + suffix)
        logging.info('Summoners: \n' + str(summoners_df.head(10)))
        logging.info('Monsters: \n' + str(monsters_df.head(10)))
    else:
        logging.info('No battles found for match type: ' + str(match_type.value))
