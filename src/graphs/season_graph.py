import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.static.static_values_enum import Leagues


def plot_season_stats_battle(season_df, theme):
    season_df = season_df.sort_values(by=['season'])
    season_df = season_df.dropna(subset=['rating'])
    season_df['win_pct'] = season_df.apply(lambda row: (row.wins / row.battles * 100), axis=1)

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    trace3 = go.Scatter(x=season_df.season,
                        y=season_df.win_pct,
                        mode='lines+markers',
                        name='win percentage')
    trace4 = go.Scatter(x=season_df.season,
                        y=season_df.battles,
                        mode='lines+markers',
                        name='battles')
    trace5 = go.Scatter(x=season_df.season,
                        y=season_df.wins,
                        mode='lines+markers',
                        name='wins')
    fig.add_trace(trace3, secondary_y=True)
    fig.add_trace(trace4)
    fig.add_trace(trace5)
    fig.update_xaxes(showgrid=True, gridwidth=1)  # , gridcolor=GRID_COLOR)
    fig.update_yaxes(showgrid=True, gridwidth=1)  # , gridcolor=GRID_COLOR)

    fig.update_layout(
        template=theme,
        # paper_bgcolor=PAPER_BGCOLOR,
        # plot_bgcolor=PLOT_BGCOLOR,
        # font=TEXT_FONT,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=10, r=10),
        xaxis=dict(
            tickvals=season_df.season,
        ),
        yaxis1=dict(
            # zerolinecolor=GRID_COLOR,
            showgrid=False,
            range=[0, season_df.battles.max() + 20],
            title='battles',
        ),
        yaxis2=dict(
            # zerolinecolor=GRID_COLOR,
            showgrid=False,
            overlaying='y',
            side='right',
            anchor='x2',
            range=[0, 100],
            title='win (%)'),
    )
    return fig


def plot_season_stats_rating(season_df, theme):
    season_df = season_df.sort_values(by=['season'])
    season_df = season_df.dropna(subset=['rating'])
    season_df = season_df.astype({'league': 'int'})
    season_ratings = [0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 5100]
    season_df['end_league_rating'] = season_df.apply(lambda row: season_ratings[row.league], axis=1)

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    trace1 = go.Scatter(x=season_df.season,
                        y=season_df.rating,
                        mode='lines+markers',
                        name='end rating',
                        line=dict(color='firebrick', width=2),
                        )
    trace2 = go.Bar(x=season_df.season,
                    y=season_df.rating,
                    showlegend=False,
                    name='not displayed ony to create secondary axis',
                    opacity=0,
                    )

    trace3 = go.Bar(x=season_df.season,
                    y=season_df.end_league_rating,
                    name='end league',
                    offset=-0.3,
                    width=0.6,
                    marker=dict(
                        color='rgb(8,48,107)',
                        line_color='rgb(8,48,107)',
                        line_width=1),
                    opacity=1,
                    )

    fig.add_trace(trace1, secondary_y=True)
    fig.add_trace(trace2)
    fig.add_trace(trace3)

    fig.update_layout(
        template=theme,
        margin=dict(l=10, r=10),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            tickvals=season_df.season,
        ),

        yaxis2=dict(
            showgrid=True,
            title='rating',
            gridwidth=1,
            nticks=25,
            range=[0, season_df.rating.max() * 1.05]
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=False,
            title='league',
            range=[0, season_df.rating.max() * 1.05],
            tickvals=[0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 9999],
            ticktext=[Leagues(0).name,
                      Leagues(1).name,
                      Leagues(2).name,
                      Leagues(3).name,
                      Leagues(4).name,
                      Leagues(5).name,
                      Leagues(6).name,
                      Leagues(7).name,
                      Leagues(8).name,
                      Leagues(9).name,
                      Leagues(10).name,
                      Leagues(11).name,
                      Leagues(12).name,
                      Leagues(13).name,
                      Leagues(14).name,
                      Leagues(15).name],
        ),
    )

    return fig


def get_season_ids_range(df_array):
    all_season_ids = set()
    for df in df_array:
        if 'season_id' in df:
            all_season_ids.update(df.season_id.unique())
    min_season_id = min(all_season_ids)
    max_season_id = max(all_season_ids)
    return set(range(min_season_id, max_season_id + 1))


def plot_season_stats_earnings(season_df_sps,
                               season_df_dec,
                               season_df_merits,
                               season_df_unclaimed_sps,
                               season_df_glint,
                               theme):
    # Data consistency
    columns_dec = [
        'reward',
        'quest_rewards',
        'season_rewards',
        'rental_payment',
        'earn_rental_payment',
        'cost_rental_payment',
        'rental_payment_fees',
        'market_rental',
        'rental_refund',
        'tournament_prize',
        'enter_tournament',
        'modern_leaderboard_prizes',
        'wild_leaderboard_prizes']
    columns_sps = [
        'claim_staking_rewards',
        'token_award',
        'tournament_prize',
        'token_transfer_multi',
        'enter_tournament']
    columns_merits = [
        'quest_rewards',
        'season_rewards',
        'brawl_prize']
    columns_glint = [
        'ranked_rewards',
        'season_rewards',
    ]

    if not season_df_dec.empty:
        season_df_dec = season_df_dec.copy().sort_values(by=['season_id']).fillna(0)
        season_df_dec['total'] = season_df_dec.filter(columns_dec).sum(axis=1, numeric_only=True)
    else:
        season_df_dec['season_id'] = []
        season_df_dec['total'] = []

    season_df_sps_combined = pd.DataFrame()
    season_df_sps_combined['season_id'] = []
    season_df_sps_combined['total'] = []
    if not season_df_sps.empty:
        season_df_sps_combined = season_df_sps.copy().sort_values(by=['season_id']).fillna(0)
        season_df_sps_combined['total'] = season_df_sps.filter(columns_sps).sum(axis=1, numeric_only=True)

    if not season_df_unclaimed_sps.empty:
        season_df_sps_combined['total_sps'] = season_df_sps_combined['total']
        season_df_unclaimed_sps = season_df_unclaimed_sps.copy().sort_values(by=['season_id']).fillna(0)
        season_df_unclaimed_sps['total_unclaimed_sps'] = (season_df_unclaimed_sps.drop(['season_id'], axis=1)
                                                          .sum(axis=1, numeric_only=True))
        season_df_sps_combined = season_df_sps_combined.merge(season_df_unclaimed_sps, on=['season_id', 'player'])
        season_df_sps_combined['total'] = season_df_sps_combined.total_sps + season_df_sps_combined.total_unclaimed_sps

    if not season_df_merits.empty:
        season_df_merits = season_df_merits.copy().sort_values(by=['season_id']).fillna(0)
        season_df_merits['total'] = season_df_merits.filter(columns_merits).sum(axis=1, numeric_only=True)
    else:
        season_df_merits['season_id'] = []
        season_df_merits['total'] = []

    if not season_df_glint.empty:
        season_df_glint = season_df_glint.copy().sort_values(by=['season_id']).fillna(0)
        season_df_glint['total'] = season_df_glint.filter(columns_glint).sum(axis=1, numeric_only=True)
    else:
        season_df_glint['season_id'] = []
        season_df_glint['total'] = []

    trace1 = go.Scatter(x=season_df_dec.season_id,
                        y=season_df_dec.total,
                        mode='lines+markers',
                        name='DEC total (earnings - payments)',
                        line=dict(color='royalblue'))

    trace2 = go.Scatter(x=season_df_merits.season_id,
                        y=season_df_merits.total,
                        mode='lines+markers',
                        name='MERITS  total (earnings)',
                        line=dict(color='red', width=2))

    trace3 = go.Scatter(x=season_df_sps_combined.season_id,
                        y=season_df_sps_combined.total,
                        mode='lines+markers',
                        name='SPS total (earnings - payments)',
                        line=dict(color='lightgreen', width=2))

    # fill glint dataframe with other season_id.
    season_range = get_season_ids_range([season_df_dec, season_df_merits, season_df_sps_combined, season_df_glint])
    season_df_glint = season_df_glint.set_index('season_id').reindex(season_range, fill_value=0).reset_index()
    season_df_glint = season_df_glint.copy().sort_values(by=['season_id']).fillna(0)

    trace4 = go.Scatter(x=season_df_glint.season_id,
                        y=season_df_glint.total,
                        mode='lines+markers',
                        name='GLINT (ranked + season rewards) ',
                        line=dict(color='steelblue', width=2))

    titles = []
    traces = []
    tick_values_arr = []
    if season_df_dec.total.sum() != 0:
        titles.append('DEC')
        traces.append(trace1)
        tick_values_arr.append(season_df_dec.season_id)
    if season_df_merits.total.sum() != 0:
        titles.append('MERITS')
        traces.append(trace2)
        tick_values_arr.append(season_df_merits.season_id)
    if season_df_sps_combined.total.sum() != 0:
        titles.append('SPS')
        traces.append(trace3)
        tick_values_arr.append(season_df_sps_combined.season_id)
    if season_df_glint.total.sum() != 0:
        titles.append('GLINT')
        traces.append(trace4)
        tick_values_arr.append(season_df_glint.season_id)

    fig = make_subplots(rows=len(titles), cols=1, row_heights=[800] * len(titles))

    for i, trace in enumerate(traces):
        fig.add_trace(trace, row=i + 1, col=1)

    for i, tick_values in enumerate(tick_values_arr):
        xaxis_name = f"xaxis{i + 1}" if i > 0 else "xaxis"
        yaxis_name = f"yaxis{i + 1}" if i > 0 else "yaxis"
        fig.update_layout(
            {
                xaxis_name: dict(
                    showgrid=True,
                    gridwidth=1,
                    tickvals=tick_values,
                ),
                yaxis_name: dict(
                    title=titles[i],
                    side='right',
                )
            }
        )

    fig.update_layout(
        template=theme,
        height=480 * len(traces),  # px
        margin=dict(l=10, r=10),
        legend=dict(
            x=0,
            y=1,
            font=dict(
                family='Courier',
                size=12,
                color='black'
            ),
            bgcolor='LightSteelBlue',
            bordercolor='Black',
            borderwidth=2
        ),
    )

    return fig


def plot_season_stats_earnings_all(season_df,
                                   title,
                                   theme,
                                   skip_zero=True):
    if skip_zero:
        season_df = season_df.loc[:, (season_df.sum(axis=0) != 0.0)]

    # Sort the columns alphabetically
    season_df = season_df.reindex(sorted(season_df.columns), axis=1)

    markers = False if len(season_df) > 1 else True
    fig = px.line(season_df,
                  x='season_id',
                  y=season_df.columns,
                  markers=markers,
                  title=title)

    fig.update_layout(
        template=theme,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=season_df.season_id,
        ),

    )
    return fig
