import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from aio import ThemeSwitchAIO
from dash import html, Output, Input, ctx, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Trigger
from dash_iconify import DashIconify

from main import app
from src import season_balances_info, season_battle_info
from src.configuration import config, store, progress
from src.graphs import season_graph
from src.utils import store_util, chart_util, progress_util

layout = dbc.Container([
    dbc.Row([
        html.H1('Season statistics'),
        dbc.Col([
            dbc.Row(
                dbc.Button(
                    'Update seasons',
                    id='update-season-btn',
                    color='primary',
                    n_clicks=0,
                    style={'width': '30%'},
                    className='mb-3',
                ),
            ),
            dbc.Row(
                dbc.InputGroup(
                    [
                        dbc.InputGroupText('Account'),
                        dcc.Dropdown(store_util.get_account_names(),
                                     value=store_util.get_first_account_name(),
                                     id='dropdown-user-selection',
                                     className='dbc',
                                     style={'width': '70%'},
                                     ),

                    ],
                    className='mb-3',
                )
            ),
        ]),
        dbc.Col(
            dbc.Accordion(
                dbc.AccordionItem([
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText('Accounts'),
                            dcc.Dropdown(
                                multi=True,
                                id='dropdown-user-selection-season',
                                className='dbc',
                                style={'width': '70%'},
                            ),
                        ], className='mb-3',
                    ),
                    dbc.Col([
                        dbc.Button('Generate', id='generate-blog', className='mb-3'),
                        dbc.Button('Copy to Clipboard', id='copy-to-clipboard', className='mb-3')]
                    ),
                ], title='Generate last season blog',
                ),
                start_collapsed=True,
            ), className='mb-3'),
    ]),

    dbc.Row([
        dbc.Col(html.H1('Modern')),
        dbc.Col(html.H1('Wild')),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='modern-season-rating-graph'),
        ),
        dbc.Col(
            dcc.Graph(id='wild-season-rating-graph'),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='modern-season-battle-graph'),
        ),
        dbc.Col(
            dcc.Graph(id='wild-season-battle-graph'),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='total-balance-graph'),
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
                             id='dropdown-token-selection',
                             className='dbc'),
                ),
        dbc.Col(dcc.RadioItems(options=['Skip Zeros', 'Keep Zeros'],
                               value='Skip Zeros',
                               id='dropdown-skip-zero-selection',
                               className='dbc'),
                ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='total-all-balance-graph'),
        ),
    ]),

    dcc.Store(id='trigger-season-update'),
    dcc.Store(id='hive-blog-content'),

])


@app.callback(Output('dropdown-user-selection-season', 'value'),
              Output('dropdown-user-selection-season', 'options'),
              Input('trigger-daily-update', 'data'),
              )
def update_user_list(tigger):
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(
    Output('trigger-season-update', 'data'),
    Input('update-season-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    progress_util.update_season_msg('Start season update')

    if 'update-season-btn' == ctx.triggered_id:
        progress_util.update_season_msg('Update season button was clicked')
        season_balances_info.update_season_balances_store()
        season_battle_info.update_season_battle_store()
        store_util.save_stores()
        progress_util.update_season_msg('Done')
        return True
    return False


@app.callback(
    Output('generate-blog', 'disabled'),
    Output('update-season-btn', 'disabled'),
    Input('generate-blog', 'n_clicks'),
    Input('update-season-btn', 'n_clicks'),
)
def validate_buttons(n_clicks_generate_blog, n_clicks_update_season_btn):
    if not ctx.triggered_id:
        raise PreventUpdate

    return True, True


@app.callback(
    Output('generate-blog', 'disabled'),
    Output('update-season-btn', 'disabled'),
    Trigger('interval-season', 'n_intervals')
)
def check_button_status(count):
    if progress.progress_season_txt:
        return True, True
    else:
        return False, False


@app.callback(
    Output('copy-to-clipboard', 'disabled'),
    Input('hive-blog-content', 'data')
)
def update_copy_to_clipboard(hive_blog):
    if not hive_blog:
        return True
    else:
        return False
    # TODO put it to the clipbaord


@app.callback(Output('modern-season-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_graph(account, season_tigger, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_modern_battle_info.empty or \
            store.season_modern_battle_info.loc[(store.season_modern_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output('wild-season-battle-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_battle_graph(account, season_trigger, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_wild_battle_info.empty or \
            store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[
            (store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output('modern-season-battle-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_battle_graph(account, season_tigger, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_modern_battle_info.empty or \
            store.season_modern_battle_info.loc[(store.season_modern_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output('wild-season-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_graph(account, season_trigger, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_wild_battle_info.empty or \
            store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output('total-balance-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(account, season_trigger, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
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


@app.callback(Output('total-all-balance-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('dropdown-token-selection', 'value'),
              Input('dropdown-skip-zero-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_all_graph(account, token, skip_zero, season_trigger, toggle):
    if skip_zero == 'Skip Zeros':
        skip_zero = True
    else:
        skip_zero = False

    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if token == 'SPS':
        if store.season_sps.empty or store.season_sps.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_sps.loc[(store.season_sps.player == account)].copy()
    elif token == 'SPS BATTLE':
        if store.season_unclaimed_sps.empty or store.season_unclaimed_sps.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_unclaimed_sps.loc[(store.season_unclaimed_sps.player == account)].copy()
    elif token == 'CREDITS':
        if store.season_credits.empty or store.season_credits.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_credits.loc[(store.season_credits.player == account)].copy()
    elif token == 'MERITS':
        if store.season_merits.empty or store.season_merits.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_merits.loc[(store.season_merits.player == account)].copy()
    elif token == 'VOUCHERS':
        if store.season_vouchers.empty or store.season_vouchers.loc[(store.season_sps.player == account)].empty:
            return chart_util.blank_fig(theme)
        season_df = store.season_vouchers.loc[(store.season_vouchers.player == account)].copy()
    elif token == 'DEC':
        if store.season_dec.empty or store.season_dec.loc[(store.season_sps.player == account)].empty:
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

