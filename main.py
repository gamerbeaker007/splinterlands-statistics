import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash

from src import battle_store, collection_store
from src.pages import navigation
from src.utils import store_util

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"


def main():
    store_util.load_stores()
    collection_store.update_collection()
    battle_store.process_battles()
    store_util.save_stores()

    load_figure_template(["cyborg", "minty"])
    app = Dash(__name__,
               external_stylesheets=[dbc.themes.CYBORG, dbc_css],
               meta_tags=[{"name": "viewport", "content": "width=device-width"}],
               suppress_callback_exceptions=True
               )


    app.layout = navigation.layout

    app.run_server(debug=True)


if __name__ == '__main__':
    main()
