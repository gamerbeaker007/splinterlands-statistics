import dash_bootstrap_components as dbc
from dash import html, Output, Input, ctx, dcc
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Trigger

from main import app
from src import season_balances_info, market_info
from src.configuration import store, progress
from src.pages.navigation_pages import nav_ids
from src.pages.season_pages import season_ids
from src.utils import store_util, progress_util, tournaments_info, hive_blog
from src.utils.trace_logging import measure_duration

layout = dbc.Accordion(
    dbc.AccordionItem([
        dcc.Store(id=season_ids.hive_blog_content),
        dbc.Row(
            dbc.InputGroup(
                [
                    dbc.InputGroupText('Accounts'),
                    dcc.Dropdown(
                        multi=True,
                        id=season_ids.dropdown_user_selection_season_blog,
                        className='dbc',
                    ),
                ], className='mb-3',
            ),
        ),
        dbc.Row([
            dbc.Col(dbc.Button('Generate', id=season_ids.generate_blog, className='mb-3'), width='auto'),
            dbc.Col(html.Div(id=season_ids.clipboard_div,
                             style={'display': 'none'},
                             children=dcc.Clipboard(id=season_ids.copy_to_clipboard, style={'fontSize': 25})
                             ),
                    )

        ]),
        dbc.Row([
            html.Div(id=season_ids.error_hive_blog),
            html.Div(id=season_ids.text_output_temp)
        ]),
    ], title='Generate last season blog',
    ),
    start_collapsed=True,
),


@app.callback(
    Output(season_ids.hive_blog_content, 'data'),
    Output(season_ids.error_hive_blog, 'children'),
    Input(season_ids.generate_blog, 'n_clicks'),
    Input(season_ids.dropdown_user_selection_season_blog, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def generate_hive_blog(n_clicks, users):
    if season_ids.generate_blog == ctx.triggered_id:
        if not users:
            return None, html.P(html.Div('No accounts selected', className='text-warning'))
        previous_season_id = store.season_end_dates.id.max() - 1
        sps_df = store_util.get_last_season_values(store.season_sps, users)

        for account in users:
            player_spd_df = sps_df.loc[sps_df.player == account]
            if player_spd_df.empty or not (player_spd_df.season_id == previous_season_id).all():
                return None, html.P(
                    html.Div('Latest season information is missing, use update season first', className='text-warning'))

        progress_util.set_season_title('Generate hive blog')
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

        progress_util.set_season_title('Generate hive blog finished ')
        progress_util.update_season_msg('Done')
        return post, ''
    return None, ''


@app.callback(
    Output(season_ids.dropdown_user_selection_season_blog, 'value'),
    Output(season_ids.dropdown_user_selection_season_blog, 'options'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_user_list(tigger):
    return store_util.get_last_portfolio_selection(), store_util.get_account_names()


@app.callback(
    Output(season_ids.generate_blog, 'disabled'),
    Output(season_ids.update_season_btn, 'disabled'),
    Input(season_ids.generate_blog, 'n_clicks'),
    Input(season_ids.update_season_btn, 'n_clicks'),
)
@measure_duration
def validate_buttons(n_clicks_generate_blog, n_clicks_update_season_btn):
    if not ctx.triggered_id:
        raise PreventUpdate

    return True, True


@app.callback(
    Output(season_ids.generate_blog, 'disabled'),
    Output(season_ids.update_season_btn, 'disabled'),
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
    Output(season_ids.copy_to_clipboard, 'content'),
    Output(season_ids.clipboard_div, 'style'),
    Input(season_ids.hive_blog_content, 'data')
)
@measure_duration
def update_copy_to_clipboard(hive_blog_txt):
    if not hive_blog_txt:
        return '', {'display': 'none'}
    else:
        return hive_blog_txt, {'display': 'block'}


@app.callback(
    Output(season_ids.text_output_temp, 'children'),
    Input(season_ids.copy_to_clipboard, 'n_clicks')
)
@measure_duration
def update_copy_to_clipboard(n_clicks):
    if ctx.triggered_id == season_ids.copy_to_clipboard:
        return html.P('Text is copied to clipboard')
