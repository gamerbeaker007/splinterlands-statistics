import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, Output, Input, ctx, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Trigger

from main import app
from src import season_balances_info, season_battle_info, market_info
from src.configuration import store, progress
from src.graphs import season_graph
from src.pages.navigation_pages import nav_ids
from src.utils import store_util, chart_util, progress_util, hive_blog, tournaments_info

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
                    dbc.Row(
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText('Accounts'),
                                dcc.Dropdown(
                                    multi=True,
                                    id='dropdown-user-selection-season',
                                    className='dbc',
                                ),
                            ], className='mb-3',
                        ),
                    ),
                    dbc.Row([
                        dbc.Col(dbc.Button('Generate', id='generate-blog', className='mb-3'), width='auto'),
                        dbc.Col(html.Div(id="clipboard-div",
                                         style={'display': 'none'},
                                         children=dcc.Clipboard(id="copy-to-clipboard", style={"fontSize": 25})
                                         ),
                                )

                    ]),
                    dbc.Row([
                        html.Div(id='error-hive-blog'),
                        html.Div(id='text-output-temp')
                    ]),
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
              Input(nav_ids.trigger_daily, 'data'),
              )
def update_user_list(tigger):
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(
    Output('trigger-season-update', 'data'),
    Input('update-season-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    if 'update-season-btn' == ctx.triggered_id:
        progress_util.set_season_title("Season update process initiated")
        progress_util.update_season_msg('Start season update')
        progress_util.update_season_msg('Update season button was clicked')
        season_balances_info.update_season_balances_store()
        season_battle_info.update_season_battle_store()
        store_util.save_stores()
        progress_util.set_season_title("Season update done")
        progress_util.update_season_msg('Done')
        return True
    return False


@app.callback(
    Output('hive-blog-content', 'data'),
    Output('error-hive-blog', 'children'),
    Input('generate-blog', 'n_clicks'),
    Input('dropdown-user-selection-season', 'value'),
    prevent_initial_call=True,
)
def generate_hive_blog(n_clicks, users):
    if 'generate-blog' == ctx.triggered_id:
        if not users:
            return None, html.P(html.Div("No accounts selected", className='text-warning'))
        previous_season_id = store.season_end_dates.id.max() - 1
        sps_df = store_util.get_last_season_values(store.season_sps, users)

        for account in users:
            player_spd_df = sps_df.loc[sps_df.player == account]
            if player_spd_df.empty or not (player_spd_df.season_id == previous_season_id).all():
                return None, html.P(
                    html.Div("Latest season information is missing, use update season first", className='text-warning'))

        progress_util.set_season_title("Generate hive blog")
        progress_util.update_season_msg('Start collecting last season data')
        season_info_store = {
            'sps': sps_df,
            'dec': store_util.get_last_season_values(store.season_dec, users),
            'merits': store_util.get_last_season_values(store.season_merits, users),
            'credits': store_util.get_last_season_values(store.season_credits, users),
            'vouchers': store_util.get_last_season_values(store.season_vouchers, users),
            'unclaimed_sps': store_util.get_last_season_values(store.season_unclaimed_sps, users),
            'modern_battle': store_util.get_last_season_values(store.season_modern_battle_info, users, 'season'),
            'wild_battle': store_util.get_last_season_values(store.season_wild_battle_info, users, 'season')
        }

        start_date, end_date = season_balances_info.get_start_end_time_season(previous_season_id)
        tournaments_info_dict = {}
        purchases_dict = {}
        sold_dict = {}
        last_season_rewards_dict = {}
        for account_name in users:
            # get tournament information
            progress_util.update_season_msg('Collecting tournament information for: ' + str(account_name))
            tournaments_info_dict[account_name] = tournaments_info.get_tournaments_info(account_name,
                                                                                        start_date,
                                                                                        end_date)

            progress_util.update_season_msg('Collecting bought and sold cards for: ' + str(account_name))
            purchases_dict[account_name], sold_dict[account_name] = market_info.get_purchased_sold_cards(account_name,
                                                                                                         start_date,
                                                                                                         end_date)

            # get last season rewards
            progress_util.update_season_msg('Collecting last season reward for: ' + str(account_name))
            last_season_rewards_dict[account_name] = market_info.get_last_season_player_history_rewards(account_name,
                                                                                                        start_date,
                                                                                                        end_date,
                                                                                                        previous_season_id)

        # print single post for each account
        post = hive_blog.write_blog_post(users,
                                         season_info_store,
                                         last_season_rewards_dict,
                                         tournaments_info_dict,
                                         purchases_dict,
                                         sold_dict,
                                         previous_season_id)

        progress_util.set_season_title("Generate hive blog finished ")
        progress_util.update_season_msg('Done')
        return post, ""
    return None, ""


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
    Trigger(nav_ids.interval_global, 'n_intervals')
)
def check_button_status():
    if progress.progress_season_txt:
        return True, True
    else:
        generate_blog_disabled = False
        if store.season_sps.empty:
            generate_blog_disabled = True

        return generate_blog_disabled, False


@app.callback(
    Output('copy-to-clipboard', 'content'),
    Output('clipboard-div', 'style'),
    Input('hive-blog-content', 'data')
)
def update_copy_to_clipboard(hive_blog_txt):
    if not hive_blog_txt:
        return "", {'display': 'none'}
    else:
        return hive_blog_txt, {'display': 'block'}


@app.callback(
    Output('text-output-temp', 'children'),
    Input('copy-to-clipboard', 'n_clicks')
)
def update_copy_to_clipboard(n_clicks):
    if ctx.triggered_id == 'copy-to-clipboard':
        return html.P("Text is copied to clipboard")


@app.callback(Output('modern-season-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input('theme-store', 'data'),
              )
def update_modern_graph(account, season_tigger, theme):
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
              Input('theme-store', 'data'),
              )
def update_wild_battle_graph(account, season_trigger, theme):
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
              Input('theme-store', 'data'),
              )
def update_modern_battle_graph(account, season_tigger, theme):
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
              Input('theme-store', 'data'),
              )
def update_wild_graph(account, season_trigger, theme):
    if store.season_wild_battle_info.empty or \
            store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output('total-balance-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input('theme-store', 'data'),
              )
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


@app.callback(Output('total-all-balance-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input('dropdown-token-selection', 'value'),
              Input('dropdown-skip-zero-selection', 'value'),
              Input('trigger-season-update', 'data'),
              Input('theme-store', 'data'),
              )
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
