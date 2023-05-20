import dash_bootstrap_components as dbc
from dash import Dash
from dash_bootstrap_templates import load_figure_template

from src import battle_store, collection_store, balances_info
from src.configuration import config
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


def main():
    store_util.load_stores()
    # balances_info.get_balances()
    collection_store.update_collection()
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
