import pandas as pd

from src.static import static_values_enum
from src.static.static_values_enum import Leagues

credit_icon = "![credit.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/" \
              "AK3iY7Tb28oEV8oALeHvUbBpKjWxvADTHcaqtPSL4C2YzcJ4oZLp36MAiX3qGNw.png)"
dec_icon = "![dec.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/" \
           "AJoDPJLp3GXfJPTZijeTGTaHE5K7vzdhCXUedhPRnp6kKhanQnpfwzfnemFdz2x.png)"
sps_icon = "![sps.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/" \
           "AKNLw1pd6ryatb2Rg9VHbWEWWUMupgMEtxYsJyxckcGH1Hb7YoxC1cFdNv37tW3.png)"
voucher_icon = "![voucher.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/" \
               "Eo8RPwT4kQnGyvkNp9Vx1kLpFYYVhKSy88Fsy7YrAStKwrHCRX6GNvhywGxPbQpW2bu.png)"
glint_icon = "![glint.png](https://images.hive.blog/20x0/" \
             "https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/shop/ranked/icon_resource_glint_small.png"
merits_icon = "![merits.png](https://images.hive.blog/20x0/" \
              "https://d36mxiodymuqjm.cloudfront.net/website/icons/img_merit_256.png)"
gold_potion_icon = ("![alchemy.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/"
                    "AK6ZKi4NWxuWbnhNc1V3k9DeqiqhTvmcenpsX5xhHUFdBGEYTMfMpsnC9aHL7R2.png)")
legendary_potion_icon = ("![legendary.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/"
                         "beaker007/AK3gbhdHjfaQxKVM39VfeHCw25haYejvUT17E8WBgveTKY5rucpRY7AbjgsAhdu.png)")
packs_icon = ("![chaosPack.png](https://images.hive.blog/20x0/https://files.peakd.com/file/peakd-hive/beaker007/"
              "Eo8M4f1Zieju9ibwbs6Tnp3KvN9Kb93HkqwMi3FqanTmV2XoNw7pmV4MbjDSxbgiSdo.png)")

intro_img = ("https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/beaker007/"
             "23tvcWHTtW5SAv63Z2J86Zuyvn5Jk2BQQ5qBQrGBvv5hRm1DUaVKJN4Z8X9eFfSokovT1.png")

earnings_divider = ("![Earnings divider.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                    "23u5tAfbYKhy3zti8o5cVxxgE2LfnjkAV4xZtm1CLAqpJL9zzEF67C7Ec8Tx6b7odFvvK.png)")
market_divider = ("![Card Market divider.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                  "23tGyBstuQdzC1Pjv1CiAvt9S3W6sfo5qzCTa6Uv2mQTpfHkwkQ89YxncGYmqsrpynjEv.png)")
tournament_divider = ("![tournament divider1.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                      "23u5vZxRCDsEy53q1Rd2sXkXvnAg94fBPj2kCVNoPnjVDiyQfiPecgCJMvoSdqwe4vjQp.png)")
closing_notes_divider = ("![Closing notes divider.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                         "23tSMhwJoyukZ42QAed1tFdaMc2XGwQZXAoTga9AByndMur5RT4oj5rMFeNJXwBeXr4tP.png)")
season_overview_divider = ("![Season summary divider.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                           "23tSKXK2kCpyZXosK34FeU6MPbw4RGCrrs7TY1tgy4k5Lgndj2JNPEbpjr8JAgQ7kW8v1.png)")
season_result_divider = ("![Season result divider.png](https://files.peakd.com/file/peakd-hive/beaker007/"
                         "23tGwQHB4Z1zXu1MnXFvSF7REdndP7Gu67aQgWuwp9VoWurqjvGq81w2M6WkfCtovhXo4.png)")

git_repo_link = "[git-repo](https://github.com/gamerbeaker007/splinterlands-statistics)"
beneficiaries_img = ("https://images.hive.blog/0x0/https://files.peakd.com/file/peakd-hive/beaker007/"
                     "23tkhySrnBbRV3iV2aD2jH7uuYJuCsFJF5j8P8EVG1aarjqSR7cRLRmuTDhji5MnTVKSM.png")

referral_link = "[beaker007](https://splinterlands.com?ref=beaker007)"


def get_last_season_statistics_table(last_season_wild_battles, last_season_modern_battles):
    if not last_season_wild_battles.empty and not last_season_wild_battles.rating.isna().values[0]:
        last_season_wild_battles = last_season_wild_battles.iloc[0]
        wild_league = last_season_wild_battles.league.astype(int)
        wild_battles = int(last_season_wild_battles.battles)
        wild_rank = int(last_season_wild_battles['rank'])
        wild_rating = int(last_season_wild_battles.rating)
        wild_league_name = Leagues(wild_league).name
        wild_max_rating = int(last_season_wild_battles.max_rating)
        wild_win = int(last_season_wild_battles.wins)
        wild_win_pct = round((wild_win / wild_battles * 100), 2)
        wild_longest_streak = int(last_season_wild_battles.longest_streak)
    else:
        wild_league = 0
        wild_league_name = "NA"
        wild_battles = "NA"
        wild_rank = "NA"
        wild_rating = "NA"
        wild_max_rating = "NA"
        wild_win = "NA"
        wild_win_pct = "NA"
        wild_longest_streak = "NA"

    if not last_season_modern_battles.empty and not last_season_modern_battles.rating.isna().values[0]:
        last_season_modern_battles = last_season_modern_battles.iloc[0]
        modern_league = last_season_modern_battles.league.astype(int)
        modern_battles = int(last_season_modern_battles.battles)
        modern_rank = int(last_season_modern_battles['rank'])
        modern_rating = int(last_season_modern_battles.rating)
        modern_league_name = Leagues(modern_league).name
        modern_max_rating = int(last_season_modern_battles.max_rating)
        modern_win = int(last_season_modern_battles.wins)
        modern_win_pct = round((modern_win / modern_battles * 100), 2)
        modern_longest_streak = int(last_season_modern_battles.longest_streak)
    else:
        modern_league = 0
        modern_league_name = "NA"
        modern_battles = "NA"
        modern_rank = "NA"
        modern_rating = "NA"
        modern_max_rating = "NA"
        modern_win = "NA"
        modern_win_pct = "NA"
        modern_longest_streak = "NA"

    wild_league_logo = ("https://images.hive.blog/75x0/https://d36mxiodymuqjm.cloudfront.net/website/icons/leagues/"
                        "wild_150/league_") + str(wild_league) + ".png"
    modern_league_logo = ("https://images.hive.blog/75x0/https://d36mxiodymuqjm.cloudfront.net/website/icons/leagues/"
                          "modern_150/league_") + str(modern_league) + ".png"
    extra_space = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    result = ("| Statistic |  " + wild_league_logo + "<br>" +
              extra_space + "Wild| " + modern_league_logo + "<br>" +
              extra_space + "Modern | \n")
    result += "| - | - | - |\n"
    result += "| Battles | " + str(wild_battles) + " | "
    result += str(modern_battles) + " | \n"
    result += "| Rank | " + str(wild_rank) + " | "
    result += str(modern_rank) + " | \n"
    result += "| Rating | " + str(wild_rating) + " - " + str(wild_league_name) + " | "
    result += str(modern_rating) + " - " + str(modern_league_name) + " | \n"
    result += "| Rating High | " + str(wild_max_rating) + " | "
    result += str(modern_max_rating) + " | \n"
    result += "| Win PCT (Wins/battles * 100) | " + str(wild_win_pct) + " (" + str(wild_win) + "/" + str(
        wild_battles) + ") |"
    result += str(modern_win_pct) + " (" + str(modern_win) + "/" + str(modern_battles) + ") |\n"
    result += "| Longest Streak | " + str(wild_longest_streak) + " |"
    result += str(modern_longest_streak) + " |\n"

    return result


def get_last_season_costs_table(account, season_info_store, skip_zeros):
    costs_rows = ""
    dec_df = season_info_store['dec']
    dec_df = dec_df.loc[(dec_df.player == account)].fillna(0)
    if not dec_df.empty:
        dec_df = dec_df.iloc[0]
        if 'cost_rental_payment' in dec_df:
            costs_rows += cost_earning_row("DEC rental payments", dec_icon, dec_df.cost_rental_payment, skip_zeros)

        if 'rental_payment_fees' in dec_df:
            costs_rows += cost_earning_row("DEC rental fees", dec_icon, dec_df.rental_payment_fees, skip_zeros)
        if 'enter_tournament' in dec_df:
            costs_rows += cost_earning_row("DEC tournament entry fees", dec_icon, dec_df.enter_tournament,
                                           skip_zeros)
        if 'market_rental' in dec_df:
            costs_rows += cost_earning_row("DEC market rental", dec_icon, dec_df.market_rental, skip_zeros)
        if 'purchased_energy' in dec_df:
            costs_rows += cost_earning_row("DEC purchased energy", dec_icon,
                                           dec_df.purchased_energy, skip_zeros)
        if 'buy_market_purchase' in dec_df:
            costs_rows += cost_earning_row("DEC market buy", dec_icon, dec_df.buy_market_purchase, skip_zeros)
        if 'market_fees' in dec_df:
            costs_rows += cost_earning_row("DEC market fees", dec_icon, dec_df.market_fees, skip_zeros)
        if 'market_list_fee' in dec_df:
            costs_rows += cost_earning_row("DEC market list fee", dec_icon, dec_df.market_list_fee, skip_zeros)

    sps_df = season_info_store['sps']
    sps_df = sps_df.loc[(sps_df.player == account)].fillna(0)
    if not sps_df.empty:
        sps_df = sps_df.iloc[0]
        if 'enter_tournament' in sps_df:
            costs_rows += cost_earning_row("SPS tournament entry fees", sps_icon, sps_df.enter_tournament,
                                           skip_zeros)
        if 'delegation_modern' in sps_df:
            costs_rows += cost_earning_row("SPS ranked battle (modern) (fees)", sps_icon, sps_df.delegation_modern,
                                           skip_zeros)
        if 'delegation_wild' in sps_df:
            costs_rows += cost_earning_row("SPS ranked battle (wild) (fees)", sps_icon, sps_df.delegation_wild,
                                           skip_zeros)
        if 'delegation_focus' in sps_df:
            costs_rows += cost_earning_row("SPS daily focus (fees)", sps_icon, sps_df.delegation_focus, skip_zeros)
        if 'delegation_season' in sps_df:
            costs_rows += cost_earning_row("SPS season (fees)", sps_icon, sps_df.delegation_season, skip_zeros)
        if 'delegation_land' in sps_df:
            costs_rows += cost_earning_row("SPS land (fees)", sps_icon, sps_df.delegation_land, skip_zeros)
        if 'delegation_nightmare' in sps_df:
            costs_rows += cost_earning_row("SPS nightmare (TD) (fees)", sps_icon, sps_df.delegation_nightmare,
                                           skip_zeros)
        if 'delegation_brawl' in sps_df:
            costs_rows += cost_earning_row("SPS brawl delegation", sps_icon, sps_df.delegation_brawl, skip_zeros)

    glint_df = season_info_store['glint']
    glint_df = glint_df.loc[(glint_df.player == account)].fillna(0)
    if not glint_df.empty:
        glint_df = glint_df.iloc[0]
        if 'purchase_reward_draw' in glint_df:
            costs_rows += cost_earning_row("GLINT rewards draws", glint_icon, glint_df.purchase_reward_draw,
                                           skip_zeros)

    result = "None"
    if costs_rows != "":
        result = "| Costs |  # |\n"
        result += "| - | - |\n"
        result += costs_rows

    return result


def cost_earning_row(title, icon, value, skip_zeros):
    if skip_zeros and value == 0:
        return ""
    else:
        return "| " + str(title) + " | " + icon + " " + str(round(value, 3)) + " |\n"


def get_last_season_earnings_table(account, season_info_store, skip_zeros):
    earning_rows = ""
    dec_df = season_info_store['dec']
    dec_df = dec_df.loc[(dec_df.player == account)].fillna(0)
    if not dec_df.empty:
        dec_df = dec_df.iloc[0]
        if 'earn_rental_payment' in dec_df:
            earning_rows += cost_earning_row("DEC rental payments", dec_icon, dec_df.earn_rental_payment, skip_zeros)
        if 'sell_market_purchase' in dec_df:
            earning_rows += cost_earning_row("DEC market sell", dec_icon, dec_df.sell_market_purchase, skip_zeros)
        if 'tournament_prize' in dec_df:
            earning_rows += cost_earning_row("DEC tournament rewards", dec_icon, dec_df.tournament_prize,
                                             skip_zeros)
        if 'modern_leaderboard_prizes' in dec_df:
            earning_rows += cost_earning_row("DEC modern leaderboard rewards", dec_icon,
                                             dec_df.modern_leaderboard_prizes, skip_zeros)
        if 'leaderboard_prizes' in dec_df:
            earning_rows += cost_earning_row("DEC wild leaderboard rewards", dec_icon,
                                             dec_df.leaderboard_prizes, skip_zeros)

    sps_df = season_info_store['sps']
    sps_df = sps_df.loc[(sps_df.player == account)].fillna(0)
    if not sps_df.empty:
        sps_df = sps_df.iloc[0]
        if 'tournament_prize' in sps_df:
            earning_rows += cost_earning_row("SPS tournament rewards", sps_icon,
                                             sps_df.tournament_prize,
                                             skip_zeros)
        if 'token_transfer_multi' in sps_df:
            earning_rows += cost_earning_row("SPS tournament rewards (multi token)", sps_icon,
                                             sps_df.token_transfer_multi,
                                             skip_zeros)
        if 'claim_staking_rewards' in sps_df:
            earning_rows += cost_earning_row("SPS staking reward", sps_icon, sps_df.claim_staking_rewards,
                                             skip_zeros)
        if 'token_award' in sps_df:
            earning_rows += cost_earning_row("SPS token award (pools)", sps_icon, sps_df.token_award, skip_zeros)

    unclaimed_sps_df = season_info_store['unclaimed_sps']
    unclaimed_sps_df = unclaimed_sps_df.loc[(unclaimed_sps_df.player == account)].fillna(0)
    if not unclaimed_sps_df.empty:
        unclaimed_sps_df = unclaimed_sps_df.iloc[0]
        if 'modern' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS ranked battle (modern)", sps_icon, unclaimed_sps_df.modern,
                                             skip_zeros)
        if 'wild' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS ranked battle (wild)", sps_icon, unclaimed_sps_df.wild, skip_zeros)
        if 'focus' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS daily focus", sps_icon, unclaimed_sps_df.focus, skip_zeros)
        if 'season' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS season", sps_icon, unclaimed_sps_df.season, skip_zeros)
        if 'land' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS land", sps_icon, unclaimed_sps_df.land, skip_zeros)
        if 'nightmare' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS nightmare (TD) ", sps_icon, unclaimed_sps_df.nightmare, skip_zeros)
        if 'brawl' in unclaimed_sps_df:
            earning_rows += cost_earning_row("SPS brawl", sps_icon, unclaimed_sps_df.brawl, skip_zeros)

    merits_df = season_info_store['merits']
    merits_df = merits_df.loc[(merits_df.player == account)].fillna(0)
    if not merits_df.empty:
        merits_df = merits_df.iloc[0]
        if 'quest_rewards' in merits_df:
            earning_rows += cost_earning_row("MERITS quest reward", merits_icon, merits_df.quest_rewards, skip_zeros)
        if 'season_rewards' in merits_df:
            earning_rows += cost_earning_row("MERITS season rewards", merits_icon, merits_df.season_rewards, skip_zeros)
        if 'brawl_prize' in merits_df:
            earning_rows += cost_earning_row("MERITS brawl prizes", merits_icon, merits_df.brawl_prize, skip_zeros)

    voucher_df = season_info_store['vouchers']
    voucher_df = voucher_df.loc[(voucher_df.player == account)].fillna(0)
    if not voucher_df.empty:
        voucher_df = voucher_df.iloc[0]
        if 'claim_staking_rewards' in voucher_df:
            earning_rows += cost_earning_row("VOUCHER earned", voucher_icon, voucher_df.claim_staking_rewards,
                                             skip_zeros)
    glint_df = season_info_store['glint']
    glint_df = glint_df.loc[(glint_df.player == account)].fillna(0)
    if not glint_df.empty:
        glint_df = glint_df.iloc[0]
        if 'ranked_rewards' in glint_df:
            earning_rows += cost_earning_row("GLINT earned", glint_icon, glint_df.ranked_rewards,
                                             skip_zeros)

    result = "None"
    if earning_rows != "":
        result = "| Earnings |  # | \n"
        result += "| - | - |\n"
        result += earning_rows

    return result


def get_tournament_info(tournaments_info):
    result = "|Tournament name | League | finish / entrants | wins/losses/draws | entry fee | prize |  \n"
    result += "|-|-|-|-|-|-| \n"

    if not tournaments_info.empty:
        for index, tournament in tournaments_info.iterrows():
            if tournament.finish:
                result += "| " + tournament['name']
                result += "| " + tournament.league
                result += "| " + str(int(tournament.finish)) + " / " + str(int(tournament.num_players))
                result += "| " + str(int(tournament.wins)) + " / " + str(int(tournament.losses)) + " / " + str(
                    int(tournament.draws))
                result += "| " + tournament.entry_fee
                result += "| " + tournament.prize_qty + " " + tournament.prize_type
                result += "| \n"

        filters_sps_prizes = tournaments_info[tournaments_info.prize_type == "SPS"]
        total_sps_earned = pd.to_numeric(filters_sps_prizes[['prize_qty']].sum(1), errors='coerce').sum()

        filters_sps_entry_fee = tournaments_info[tournaments_info.entry_fee.str.contains("SPS")].copy()
        split = filters_sps_entry_fee.loc[:, 'entry_fee'].str.split(" ", expand=True)
        total_sps_fee = 0
        if not split.empty:
            filters_sps_entry_fee.loc[:, 'fee_qty'] = split[0]
            filters_sps_entry_fee.loc[:, 'fee_type'] = split[1]
            total_sps_fee = pd.to_numeric(filters_sps_entry_fee[['fee_qty']].sum(1), errors='coerce').sum()

        result += "|**Total SPS** | | | | **" + str(total_sps_fee) + "**|**" + str(total_sps_earned) + "**| \n"

    return result


def get_card_table(cards_df, print_count=False):
    base_card_url = "https://images.hive.blog/150x0/https://d36mxiodymuqjm.cloudfront.net/cards_by_level/"

    if cards_df is not None and len(cards_df) > 0:
        unique_card_list = cards_df.card_name.unique()
        temp = pd.DataFrame()
        for card_name in unique_card_list:
            temp = pd.concat([temp, pd.DataFrame({
                'card_name': card_name,
                'quantity_regular': len(cards_df[(cards_df['card_name'] == card_name) & (~cards_df['gold'])]),
                'quantity_gold': len(cards_df[(cards_df['card_name'] == card_name) & (cards_df['gold'])]),
                'edition_name': str(cards_df[(cards_df['card_name'] == card_name)].edition_name.values[0]),
                'bcx': str(cards_df[(cards_df['card_name'] == card_name) & (~cards_df['gold'])].bcx.sum()),
                'bcx_gold': str(cards_df[(cards_df['card_name'] == card_name) & (cards_df['gold'])].bcx.sum())
            }, index=[0])], ignore_index=True)

        if len(temp.index) > 5:
            result = "| | | | | |\n"
            result += "|-|-|-|-|-|\n"
        else:
            # print all in one row
            table_row = "|"
            for i in range(0, len(temp.index)):
                table_row += " |"
            result = table_row + "\n" + table_row.replace(" ", "-") + "\n"

        result += "|"
        for index, card in temp.iterrows():
            if index > 0 and index % 5 == 0:
                result += "\n"

            prefix = str(base_card_url) + str(card.edition_name) + "/" + str(card.card_name).replace(" ", "%20")
            count_str = ""
            gold_suffix = ""
            if card.quantity_regular > 0:
                bcx = str(card.bcx)
                if print_count:
                    count_str = " <br> " + str(card.quantity_regular) + "x"
            if card.quantity_gold > 0:
                gold_suffix = "_gold"
                bcx = str(card.bcx_gold)
                if print_count:
                    count_str = " <br> " + str(card.quantity_gold) + "x"

            card_image_url = prefix + "_lv1" + gold_suffix + ".png"
            result += "" + str(card_image_url) + count_str + " <br> bcx: " + str(bcx)
            result += " |"
    else:
        result = "None"
    return result


def get_rewards_potion_packs_table(last_season_rewards):
    if not last_season_rewards.empty:
        gold_potion = ("![alchemy.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/"
                       "beaker007/AK6ZKi4NWxuWbnhNc1V3k9DeqiqhTvmcenpsX5xhHUFdBGEYTMfMpsnC9aHL7R2.png)")
        legendary_potion = ("![legendary.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/"
                            "beaker007/AK3gbhdHjfaQxKVM39VfeHCw25haYejvUT17E8WBgveTKY5rucpRY7AbjgsAhdu.png)")
        packs_img = ("![chaosPack.png](https://images.hive.blog/120x0/https://files.peakd.com/file/peakd-hive/"
                     "beaker007/Eo8M4f1Zieju9ibwbs6Tnp3KvN9Kb93HkqwMi3FqanTmV2XoNw7pmV4MbjDSxbgiSdo.png)")

        potions = last_season_rewards[(last_season_rewards['type'] == 'potion')].groupby(['potion_type']).sum()
        packs = last_season_rewards[(last_season_rewards['type'] == 'pack')].groupby(['edition']).sum()
        result = "| Legendary | Gold | Packs |\n"
        result += "|-|-|-|\n"
        result += "| " + str(legendary_potion) + "<br> " + str(potions.loc['legendary'].quantity) + "x"
        result += "| " + str(gold_potion) + "<br> " + str(potions.loc['gold'].quantity) + "x"
        if packs.empty:
            result += "| " + str(packs_img) + "<br> 0x"
        else:
            result += "| " + str(packs_img) + "<br> " + str(packs.loc[7.0].quantity) + "x"

        result += "|\n"
        return result
    else:
        return "None"


def get_introduction_chapter(account_names):
    account_suffix = ""
    if len(account_names) > 1:
        account_suffix = " (" + str(get_account_names_str(account_names)) + ")"
    return intro_img + """
<br><br><br>
""" + season_overview_divider + """
# <div class="phishy"><center>Season Summary""" + str(account_suffix) + """</center></div>

"""


def get_closure_chapter():
    return """
<br><br>
""" + closing_notes_divider + """
## <div class="phishy"><center>Closing notes</center></div>
This report is generated with the splinterlands statistics tool from @beaker007 """ + git_repo_link + """.
Any comment/remarks/errors pop me a message on peakd.
If you like the content, consider adding @beaker007 as beneficiaries of your post created with the help of this tool.
""" + beneficiaries_img + """


If you are not playing splinterlands consider using my referral link """ + referral_link + """.

Thx all for reading

<center>https://d36mxiodymuqjm.cloudfront.net/website/splinterlands_logo.png</center>
"""


def get_plot_placeholder(account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"

    return """
## <div class="phishy"><center>Season overall stats and history""" + str(account_suffix) + """</center></div>

### Battles

### Earnings


"""


def get_last_season_results(season_battles_wild, season_battles_modern, previous_season_id, account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"
    return """
<br><br>
""" + season_result_divider + """
# <div class="phishy"><center>Last Season results""" + str(account_suffix) + """</center></div>
""" + str(get_last_season_statistics_table(season_battles_wild, season_battles_modern)) + """

"""


def get_tournament_results(tournaments_info, account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"

    if not tournaments_info.empty:
        return """
<br><br>
""" + tournament_divider + """
## <div class="phishy"><center>Tournaments""" + str(account_suffix) + """</center></div>
""" + str(get_tournament_info(tournaments_info)) + """

"""
    return ""


def get_last_season_earning_costs(account, season_info_store, skip_zeros, account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"

    return """
<br><br>
""" + earnings_divider + """
## <div class="phishy"><center>Earnings and costs""" + str(account_suffix) + """</center></div>
""" + str(get_last_season_earnings_table(account, season_info_store, skip_zeros)) + """

## <div class="phishy"><center>Costs</center></div>
""" + str(get_last_season_costs_table(account, season_info_store, skip_zeros)) + """
     """


def get_sub_type_sum(df, name):
    if df.empty:
        return 0
    else:
        return df.loc[df.sub_type == name].sub_type.count()


def get_reward_draws_table(df):
    result = '|' + static_values_enum.reward_draw_initiate_icon_url
    result += '|' + static_values_enum.reward_draw_adept_icon_url
    result += '|' + static_values_enum.reward_draw_veteran_icon_url
    result += '|' + static_values_enum.reward_draw_elite_icon_url
    result += '|' + static_values_enum.reward_draw_master_icon_url
    result += '|\n'
    result += '|-|-|-|-|-|\n'
    result += '| <center>Initiate: ' + str(get_sub_type_sum(df, 'initiate_draw')) + 'x</center>'
    result += '| <center>Adept: ' + str(get_sub_type_sum(df, 'adept_draw')) + 'x</center>'
    result += '| <center>Veteran: ' + str(get_sub_type_sum(df, 'veteran_draw')) + 'x</center>'
    result += '| <center> Elite: ' + str(get_sub_type_sum(df, 'elite_draw')) + 'x</center>'
    result += '| <center>Master: ' + str(get_sub_type_sum(df, 'master_draw')) + 'x</center>'
    result += '|\n'
    return result


def get_last_season_rewards(last_season_rewards, account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"

    return """
## <div class="phishy"><center>Draws purchased """ + str(account_suffix) + """</center></div>
""" + str(get_reward_draws_table(last_season_rewards)) + """

## <div class="phishy"><center>Cards earned""" + str(account_suffix) + """</center></div>
""" + str(get_card_table(last_season_rewards)) + """
    """


def get_last_season_market_transactions(purchases_cards, sold_cards, account_name=None):
    account_suffix = ""
    if account_name:
        account_suffix = " (" + str(account_name) + ")"

    return """
<br><br>
""" + market_divider + """
## <div class="phishy"><center>Cards Purchased""" + str(account_suffix) + """</center></div>
Note: Completed splex.gg and peakmonsters bids are not in this overview, those are purchased by other accounts.

""" + str(get_card_table(purchases_cards, True)) + """


## <div class="phishy"><center>Cards Sold""" + str(account_suffix) + """</center></div>
Note: Only cards that are listed and sold in this season are displayed here.
""" + str(get_card_table(sold_cards, True)) + """

"""


def get_account_introduction(account_names, previous_season_id):
    result = "Tracking my result for season " + str(previous_season_id) + " : " \
             + str(get_account_names_str(account_names)) + "\n\n"
    return result


def get_account_names_str(account_names):
    result = ""
    for account_name in account_names:
        result += str(account_name)
        if account_name != account_names[-1]:
            result += ", "
    return result


def write_blog_post(account_names,
                    season_info_store,
                    last_season_rewards_dict,
                    tournaments_info_dict,
                    purchases_cards_dict,
                    sold_cards_dict,
                    previous_season_id,
                    skip_zeros=True):
    single_account = (len(account_names) == 1)
    post = get_account_introduction(account_names, previous_season_id)
    post += get_introduction_chapter(account_names)

    wild_battle_df = season_info_store['wild_battle']
    modern_battle_df = season_info_store['modern_battle']
    for account_name in account_names:
        # If there is only one account so a single post do not use account name in post.
        if single_account:
            print_account_name = None
        else:
            print_account_name = account_name

        post += get_plot_placeholder(account_name=print_account_name)
        post += get_last_season_results(wild_battle_df.loc[wild_battle_df.player == account_name],
                                        modern_battle_df.loc[modern_battle_df.player == account_name],
                                        previous_season_id,
                                        account_name=print_account_name)
        post += get_tournament_results(tournaments_info_dict[account_name],
                                       account_name=account_name)
        post += get_last_season_earning_costs(account_name,
                                              season_info_store,
                                              skip_zeros,
                                              account_name=print_account_name)
        post += get_last_season_market_transactions(purchases_cards_dict[account_name],
                                                    sold_cards_dict[account_name],
                                                    account_name=print_account_name)
        post += get_last_season_rewards(last_season_rewards_dict[account_name],
                                        account_name=print_account_name)

        if single_account:
            post += get_closure_chapter()

    if not single_account:
        post += get_closure_chapter()
    return post
