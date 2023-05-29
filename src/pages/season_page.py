import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
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
        html.H1('Update press button'),
        dbc.Col(
            dbc.Button(
                'Pull new data',
                id='update-season-btn',
                color='primary',
                className='ms-2', n_clicks=0
            ),
            width='auto',
        ),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=store_util.get_account_names(),
                             value=store_util.get_first_account_name(),
                             id='dropdown-user-selection',
                             className='dbc'),
                ),
    ]),
    dbc.Row([
        dbc.Col(html.H1("Modern")),
        dbc.Col(html.H1("Wild")),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="modern-season-rating-graph"),
        ),
        dbc.Col(
            dcc.Graph(id="wild-season-rating-graph"),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="modern-season-battle-graph"),
        ),
        dbc.Col(
            dcc.Graph(id="wild-season-battle-graph"),
        ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="total-balance-graph"),
        ),
    ]),
    dbc.Row([
        html.H1("Detailed per token"),
        html.P("Select token"),
        html.P("Tip: Double click on the legend to view one or all"),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(options=["SPS", "SPS UNCLAIMED", "DEC", "MERITS", "VOUCHERS"],
                             value="SPS",
                             id='dropdown-token-selection',
                             className='dbc'),
                ),
        dbc.Col(dcc.RadioItems(options=["Skip Zeros", "Keep Zeros"],
                               value="Skip Zeros",
                               id='dropdown-skip-zero-selection',
                               className='dbc'),
                ),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="total-all-balance-graph"),
        ),
    ]),

    html.Div(id='hidden-div-balance'),
    html.Div(id='progress-balance'),
    dcc.Interval(id="interval-balance", interval=10000),

])


@app.callback(Output("progress-balance", "children"),
              Trigger("interval-balance", "n_intervals"))
def update_progress(interval):
    value = progress.progress_txt
    if value is None:
        raise PreventUpdate
    if value == "Done":
        progress.progress_txt = None
        return dmc.Notification(
            id="my-notification",
            title="Season update done",
            message=str(value),
            color="green",
            action="update",
            autoClose=True,
            icon=DashIconify(icon="akar-icons:circle-check"),
        )
    else:
        return dmc.Notification(
            id="my-notification",
            title="Season update process initiated",
            message=str(value),
            loading=True,
            color="orange",
            action="show",
            autoClose=9000,
        )


@app.callback(
    Output('hidden-div-balance', 'children'),
    Input('update-season-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def update_output(n_clicks):
    progress_util.set_msg("Start season update")

    if "update-season-btn" == ctx.triggered_id:
        progress_util.set_msg("Update season button was clicked")
        season_balances_info.update_season_balances_store()
        season_battle_info.update_season_battle_store()
        store_util.save_stores()
        progress_util.set_msg("Done")


@app.callback(Output('modern-season-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_modern_battle_info.empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output('wild-season-battle-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_battle_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_wild_battle_info.empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[
            (store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output('modern-season-battle-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_modern_battle_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_modern_battle_info.empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_modern_battle_info.loc[
            (store.season_modern_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_battle(season_df, theme)


@app.callback(Output('wild-season-rating-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_wild_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_wild_battle_info.empty:
        return chart_util.blank_fig(theme)
    else:
        season_df = store.season_wild_battle_info.loc[(store.season_wild_battle_info.player == account)].copy()
        return season_graph.plot_season_stats_rating(season_df, theme)


@app.callback(Output('total-balance-graph', 'figure'),
              Input('dropdown-user-selection', 'value'),
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(account, toggle):
    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_sps.empty:
        return chart_util.blank_fig(theme)
    else:
        season_df_sps = store.season_sps.loc[(store.season_sps.player == account)].copy()
        season_df_dec = store.season_dec.loc[(store.season_dec.player == account)].copy()
        season_df_merits = store.season_merits.loc[(store.season_merits.player == account)].copy()
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
              Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
              )
def update_earnings_graph(account, token, skip_zero, toggle):
    if skip_zero == "Skip Zeros":
        skip_zero = True
    else:
        skip_zero = False

    # TODO check which order callbacks are done
    theme = config.light_theme if toggle else config.dark_theme
    if store.season_sps.empty:
        return chart_util.blank_fig(theme)
    else:
        if token == "SPS":
            season_df = store.season_sps.loc[(store.season_sps.player == account)].copy()
        elif token == "MERITS":
            season_df = store.season_merits.loc[(store.season_merits.player == account)].copy()
        elif token == "SPS UNCLAIMED":
            season_df = store.season_unclaimed_sps.loc[
                (store.season_unclaimed_sps.player == account)].copy()
        elif token == "VOUCHERS":
            season_df = store.season_vouchers.loc[(store.season_vouchers.player == account)].copy()
        elif token == "DEC":
            season_df = store.season_dec.loc[(store.season_dec.player == account)].copy()
        else:
            return chart_util.blank_fig(theme)

        season_df = season_df.sort_values(by=['season_id']).fillna(0)
        season_df.drop(columns=['player'], inplace=True)
        season_df["Total"] = season_df.select_dtypes(include=['float']).sum(axis=1)

        return season_graph.plot_season_stats_earnings_all(season_df,
                                                           token,
                                                           theme,
                                                           skip_zero)
