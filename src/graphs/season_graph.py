from plotly.subplots import make_subplots

from src.static.static_values_enum import Leagues
import plotly.express as px
import plotly.graph_objects as go


def plot_season_stats_battle(season_df, theme):
    season_df = season_df.sort_values(by=['season'])
    season_df = season_df.dropna(subset=['rating'])
    season_df['win_pct'] = season_df.apply(lambda row: (row.wins / row.battles * 100), axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
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
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            tickvals=season_df.season,
        ),
        yaxis1=dict(
            # zerolinecolor=GRID_COLOR,
            showgrid=False,
            range=[0, season_df.battles.max() + 20],
            title="battles",
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


def check_data_consistency(season_df, columns):
    for column in columns:
        if column not in season_df:
            season_df[column] = season_df.get(column, 0)
    return season_df


def plot_season_stats_rating(season_df, theme):
    season_df = season_df.sort_values(by=['season'])
    season_df = season_df.dropna(subset=['rating'])
    season_df = season_df.astype({'league': 'int'})
    season_ratings = [0, 400, 700, 1000, 1300, 1600, 1900, 2200, 2500, 2800, 3100, 3400, 3700, 4200, 4700, 5100]
    season_df['end_league_rating'] = season_df.apply(lambda row: season_ratings[row.league], axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(
            tickvals=season_df.season,
        ),

        yaxis2=dict(
            showgrid=True,
            title="rating",
            gridwidth=1,
            nticks=25,
            range=[0, season_df.rating.max() * 1.05]
        ),
        yaxis=dict(
            zeroline=False,
            showgrid=False,
            title="league",
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


def plot_season_stats_earnings(season_df_sps,
                               season_df_dec,
                               season_df_merits,
                               season_df_unclaimed_sps,
                               theme,
                               skip_zeros=True):
    season_df_sps = season_df_sps.sort_values(by=['season_id']).fillna(0)
    season_df_dec = season_df_dec.sort_values(by=['season_id']).fillna(0)
    season_df_merits = season_df_merits.sort_values(by=['season_id']).fillna(0)
    season_df_unclaimed_sps = season_df_unclaimed_sps.sort_values(by=['season_id']).fillna(0)

    # Data consistency
    columns_dec = [
        'reward',
        'quest_rewards',
        'season_rewards',
        'rental_payment',
        'rental_payment_fees',
        'market_rental',
        'rental_refund',
        'tournament_prize',
        'enter_tournament',
        'modern_leaderboard_prizes',
        'wild_leaderboard_prizes',
        'market_fees',
        'market_list_fee']
    columns_unclaimed_sps = [
        'modern',
        'wild',
        'focus',
        'season',
        'brawl',
        'land',
        'nightmare']
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

    season_df_dec = check_data_consistency(season_df_dec, columns_dec)
    season_df_sps = check_data_consistency(season_df_sps, columns_sps)
    season_df_merits = check_data_consistency(season_df_merits, columns_merits)
    season_df_unclaimed_sps = check_data_consistency(season_df_unclaimed_sps, columns_unclaimed_sps)

    dec_earned = season_df_dec.reward \
                 + season_df_dec.quest_rewards \
                 + season_df_dec.season_rewards \
                 + season_df_dec.modern_leaderboard_prizes \
                 + season_df_dec.wild_leaderboard_prizes

    dec_rental_earned = season_df_dec.rental_payment + season_df_dec.rental_payment_fees
    dec_rental_payed = season_df_dec.market_rental + season_df_dec.rental_refund
    dec_market_fees = season_df_dec.market_list_fee
    dec_tournament = season_df_dec.tournament_prize + season_df_dec.enter_tournament

    sps_earned = season_df_sps.claim_staking_rewards + season_df_sps.token_award
    sps_tournament = season_df_sps.tournament_prize + \
                     season_df_sps.token_transfer_multi + \
                     season_df_sps.enter_tournament
    sps_battle_earning = season_df_unclaimed_sps.modern + \
                         season_df_unclaimed_sps.wild + \
                         season_df_unclaimed_sps.focus + \
                         season_df_unclaimed_sps.season + \
                         season_df_unclaimed_sps.brawl
    sps_rewards = season_df_unclaimed_sps.land + season_df_unclaimed_sps.nightmare

    sps_total = sps_earned + sps_tournament + sps_battle_earning + sps_rewards
    dec_total = dec_earned + dec_rental_earned + dec_rental_payed + dec_tournament + dec_market_fees
    merits_total = season_df_merits.quest_rewards + season_df_merits.season_rewards + season_df_merits.brawl_prize

    # credits_earned = season_df.credits_quest_rewards + season_df.credits_season_rewards

    # trace1 = go.Scatter(x=season_df.season, y=credits_earned, mode='lines+markers',  name='credits (quest + season reward)')
    # trace2 = go.Scatter(x=season_df.season, y=sps_earned, mode='lines+markers',  name='sps (staking + token award)')
    # trace3 = go.Scatter(x=season_df.season, y=dec_earned, mode='lines+markers',  name='dec (ranked + quest + season)')
    # trace4 = go.Scatter(x=season_df.season, y=dec_rental_earned, mode='lines+markers',  name='dec rental (payment-fees)')
    # trace5 = go.Scatter(x=season_df.season, y=dec_rental_payed, mode='lines+markers',  name='dec rental (cost-refund)')
    # trace6 = go.Scatter(x=season_df.season, y=dec_tournament, mode='lines+markers',  name='dec tournament (prize-entry)')

    trace7 = go.Scatter(x=season_df_dec.season_id,
                        y=dec_total,
                        mode='lines+markers',
                        name='DEC total (earnings - payments)',
                        line=dict(color='royalblue'))

    trace8 = go.Scatter(x=season_df_merits.season_id,
                        y=merits_total,
                        mode='lines+markers',
                        name='MERITS  total (earnings)',
                        line=dict(color='red', width=2))
    trace9 = go.Scatter(x=season_df_sps.season_id,
                        y=sps_total,
                        mode='lines+markers',
                        name='SPS total (earnings - payments)',
                        line=dict(color='lightgreen', width=2))

    titles = ["", "", ""]
    if not skip_zeros:
        titles = ["DEC", "MERITS", "SPS"]
        row_heights = [800, 800, 800]
        rows = 3
        fig = make_subplots(rows=rows, cols=1, row_heights=row_heights)
        fig.add_trace(trace7, row=1, col=1)
        fig.add_trace(trace8, row=2, col=1)
        fig.add_trace(trace9, row=3, col=1)
    else:
        total_rows = 0
        row_heights = []
        if dec_total.sum() > 0:
            total_rows += 1
            row_heights.append(800)
        if merits_total.sum() > 0:
            total_rows += 1
            row_heights.append(800)
        if sps_total.sum() > 0:
            total_rows += 1
            row_heights.append(800)

        fig = make_subplots(rows=total_rows, cols=1, row_heights=row_heights)
        rows = 0
        if dec_total.sum() > 0:
            titles[rows] = "DEC"
            rows += 1
            fig.add_trace(trace7, row=rows, col=1)
        if merits_total.sum() > 0:
            titles[rows] = "MERITS"
            rows += 1
            fig.add_trace(trace8, row=rows, col=1)
        if sps_total.sum() > 0:
            titles[rows] = "SPS"
            rows += 1
            fig.add_trace(trace9, row=rows, col=1)

    fig.update_layout(
        template=theme,
        height=1200,  # px

        legend=dict(
            x=0,
            y=1,
            font=dict(
                family="Courier",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=season_df_dec.season_id,
        ),
        yaxis=dict(
            title=titles[0],
            side="right",
        ),

        xaxis2=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=season_df_sps.season_id,
        ),
        yaxis2=dict(
            title=titles[1],
            side="right"
        ),

        xaxis3=dict(
            showgrid=True,
            gridwidth=1,
            tickvals=season_df_merits.season_id,
        ),
        yaxis3=dict(
            title=titles[2],
            side="right"
        ),
    )

    return fig


def plot_season_stats_earnings_all(season_df,
                                   title,
                                   theme,
                                   skip_zero=True):
    if skip_zero:
        for column in season_df.columns.tolist():
            if season_df[column].sum() == 0.0:
                season_df.drop(columns=[column], inplace=True)

    fig = px.line(season_df,
                  x='season_id',
                  y=season_df.columns,
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
