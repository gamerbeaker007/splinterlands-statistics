from src.pages import navigation
from src.pages.main_dash import app
from src.utils import store_util


def main():
    store_util.load_stores()
    # balances_info.get_balances()
    # collection_store.update_collection()
    # battle_store.process_battles()
    #
    # store_util.save_stores()

    app.layout = navigation.layout
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
