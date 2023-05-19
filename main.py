import dash_bootstrap_components as dbc
from dash import Dash
from dash_bootstrap_templates import load_figure_template

from src import battle_store, collection_store
from src.configuration import config, store
from src.pages import navigation
from src.static.static_values_enum import Edition
from src.utils import store_util

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template([config.dark_theme, config.light_theme])


def get_image_url(card_name, level, edition, gold):
    base_card_url = 'https://images.hive.blog/150x0/https://d36mxiodymuqjm.cloudfront.net/cards_by_level/'
    edition_name = Edition(edition).name
    prefix = str(base_card_url) + str(edition_name) + "/" + str(card_name).replace(" ", "%20")
    gold_suffix = ""
    if gold:
        gold_suffix = "_gold"

    card_image_url = str(prefix) + "_lv" + str(level) + str(gold_suffix) + ".png"
    return card_image_url


def migrate_battle_store():
    if 'uid' in store.battle_big_df.columns.to_list():
        temp_new_store = store.battle_big_df.copy()
        temp_new_store['card_detail_id'] = temp_new_store.apply(
            lambda row: store.collection_df.loc[row.uid]['card_detail_id'], axis=1)
        temp_new_store['card_name'] = temp_new_store.apply(lambda row: store.collection_df.loc[row.uid]['card_name'],
                                                           axis=1)
        temp_new_store['card_type'] = temp_new_store.apply(
            lambda row: config.card_details_df.loc[row.card_detail_id]['type'], axis=1)
        temp_new_store['xp'] = temp_new_store.apply(lambda row: store.collection_df.loc[row.uid]['xp'], axis=1)
        temp_new_store['gold'] = temp_new_store.apply(lambda row: store.collection_df.loc[row.uid]['gold'], axis=1)
        temp_new_store['level'] = temp_new_store.apply(lambda row: store.collection_df.loc[row.uid]['level'], axis=1)
        temp_new_store['edition'] = temp_new_store.apply(lambda row: store.collection_df.loc[row.uid]['edition'],
                                                         axis=1)
        temp_new_store.drop(['uid'], axis=1, inplace=True)
        store.battle_big_df = temp_new_store[['card_detail_id', 'card_name', 'card_type', 'xp', 'gold', 'level',
                                                     'edition', 'account', 'created_date', 'match_type', 'format',
                                                     'mana_cap', 'ruleset1', 'ruleset2', 'ruleset3',
                                                     'inactive', 'battle_id', 'winner', 'result']]
    pass


def main():
    store_util.load_stores()
    collection_store.update_collection()
    migrate_battle_store()
    battle_store.process_battles()

    store_util.save_stores()

    app = Dash(__name__,
               external_stylesheets=[dbc.themes.CYBORG, dbc_css],
               meta_tags=[{"name": "viewport", "content": "width=device-width"}],
               suppress_callback_exceptions=True
               )

    app.layout = navigation.layout

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
