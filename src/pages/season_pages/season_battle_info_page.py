import dash_bootstrap_components as dbc
from dash import html, Output, Input, dcc

from main import app
from src.configuration import store
from src.graphs import season_graph
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids
from src.utils import chart_util

layout = [
    dbc.Row([
        dbc.Col(html.H1('Modern')),
        dbc.Col(html.H1('Wild')),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id=season_ids.modern_season_rating_graph),
        ),
        dbc.Col(
            dcc.Graph(id=season_ids.wild_season_rating_graph),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id=season_ids.modern_season_battle_graph),
        ),
        dbc.Col(
            dcc.Graph(id=season_ids.wild_season_battle_graph),
        ),
    ])
]


@app.callback(Output(season_ids.modern_season_rating_graph, 'figure'),
              Input(season_ids.dropdown_user_selection_season, 'value'),
              Input(season_ids.trigger_season_update, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_modern_graph(account, season_tigger, theme):
    if store.season_modern_battle_info.empty or \
            store.season_modern_battle_info.loc[(store.season_modern_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output(season_ids.wild_season_battle_graph, 'figure'),
              Input(season_ids.dropdown_user_selection_season, 'value'),
              Input(season_ids.trigger_season_update, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_wild_battle_graph(account, season_trigger, theme):
    if store.season_wild_battle_info.empty or \
            store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[
            (store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output(season_ids.modern_season_battle_graph, 'figure'),
              Input(season_ids.dropdown_user_selection_season, 'value'),
              Input(season_ids.trigger_season_update, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_modern_battle_graph(account, season_tigger, theme):
    if store.season_modern_battle_info.empty or \
            store.season_modern_battle_info.loc[(store.season_modern_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output(season_ids.wild_season_rating_graph, 'figure'),
              Input(season_ids.dropdown_user_selection_season, 'value'),
              Input(season_ids.trigger_season_update, 'data'),
              Input(nav_ids.theme_store, 'data'),
              )
def update_wild_graph(account, season_trigger, theme):
    if store.season_wild_battle_info.empty or \
            store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)
