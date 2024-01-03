import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, dcc

from src.pages.main_dash import app
from src.configuration import store
from src.graphs import season_graph
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

layout = [
    dbc.Row([
        dbc.Col(
            dcc.Graph(id=season_ids.total_balance_graph),
        ),
    ]),
    dbc.Row([
        html.H1('Detailed per token'),
        html.P('Select token'),
        html.P('Tip: Double click on the legend to view one or all'),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=['SPS', 'SPS BATTLE', 'DEC', 'MERITS', 'VOUCHERS', 'CREDITS'],
                             value='SPS',
                             id=season_ids.dropdown_token_selection,
                             className='dbc'),
                ),
        dbc.Col(dcc.RadioItems(options=['Skip Zeros', 'Keep Zeros'],
                               value='Skip Zeros',
                               id=season_ids.dropdown_skip_zero_selection,
                               className='dbc'),
                ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id=season_ids.total_all_balance_graph),
        ),
    ]),

]


@app.callback(
    Output(season_ids.total_balance_graph, 'figure'),
    Input(season_ids.dropdown_user_selection_season, 'value'),
    Input(season_ids.trigger_season_update, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_earnings_graph(account, season_trigger, theme):
    if store.season_sps.empty or \
            store.season_sps.loc[(store.season_sps.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df_sps = season_df_dec = season_df_merits = season_df_unclaimed_sps = pd.DataFrame()
        if not store.season_sps.empty:
            season_df_sps = store.season_sps.loc[(store.season_sps.player == account)].copy()
        if not store.season_dec.empty:
            season_df_dec = store.season_dec.loc[(store.season_dec.player == account)].copy()
        if not store.season_merits.empty:
            season_df_merits = store.season_merits.loc[(store.season_merits.player == account)].copy()
        if not store.season_unclaimed_sps.empty:
            season_df_unclaimed_sps = store.season_unclaimed_sps.loc[
                (store.season_unclaimed_sps.player == account)].copy()

        return season_graph.plot_season_stats_earnings(season_df_sps,
                                                       season_df_dec,
                                                       season_df_merits,
                                                       season_df_unclaimed_sps,
                                                       theme)


@app.callback(
    Output(season_ids.total_all_balance_graph, 'figure'),
    Input(season_ids.dropdown_user_selection_season, 'value'),
    Input(season_ids.dropdown_token_selection, 'value'),
    Input(season_ids.dropdown_skip_zero_selection, 'value'),
    Input(season_ids.trigger_season_update, 'data'),
    Input(nav_ids.theme_store, 'data'),
)
@measure_duration
def update_earnings_all_graph(account, token, skip_zero, season_trigger, theme):
    if skip_zero == 'Skip Zeros':
        skip_zero = True
    else:
        skip_zero = False

    if token == 'SPS':
        if store.season_sps.empty or store.season_sps.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_sps.loc[(store.season_sps.player == account)].copy()
    elif token == 'SPS BATTLE':
        if store.season_unclaimed_sps.empty or \
                store.season_unclaimed_sps.loc[(store.season_unclaimed_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_unclaimed_sps.loc[(store.season_unclaimed_sps.player == account)].copy()
    elif token == 'CREDITS':
        if store.season_credits.empty or store.season_credits.loc[(store.season_credits.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_credits.loc[(store.season_credits.player == account)].copy()
    elif token == 'MERITS':
        if store.season_merits.empty or store.season_merits.loc[(store.season_merits.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_merits.loc[(store.season_merits.player == account)].copy()
    elif token == 'VOUCHERS':
        if store.season_vouchers.empty or store.season_vouchers.loc[(store.season_vouchers.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_vouchers.loc[(store.season_vouchers.player == account)].copy()
    elif token == 'DEC':
        if store.season_dec.empty or store.season_dec.loc[(store.season_dec.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_dec.loc[(store.season_dec.player == account)].copy()
    else:
        return chart_util.blank_fig(theme)

    season_df = season_df.sort_values(by=['season_id']).fillna(0)
    season_df.drop(columns=['player'], inplace=True)
    season_df['Total'] = season_df.select_dtypes(include=['float']).sum(axis=1)

    return season_graph.plot_season_stats_earnings_all(season_df,
                                                       token,
                                                       theme,
                                                       skip_zero)
