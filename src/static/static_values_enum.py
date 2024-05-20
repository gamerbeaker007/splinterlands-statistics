from enum import Enum

LAND_SWAP_FEE = 0.9  # 10 swap_fee

# league_ratings_all = [
#     0,     # Novice
#     260,   # Bronze III
#     400,   # Bronze II
#     700,   # Bronze I
#     1000,  # Silver III
#     1300,  # Silver II
#     1600,  # Silver I
#     1900,  # Gold III
#     2200,  # Gold II
#     2500,  # Gold I
#     2800,  # Diamond III
#     3100,  # Diamond II
#     3400,  # Diamond I
#     3700,  # Champion III
#     4000,  # Champion II
#     4300,  # Champion I
#     5000   # CAP for calculating rewards shares
# ]

league_ratings = [0, 260, 1000, 1900, 2800, 3700]
league_colors = ['lightgray', 'brown', 'gray', 'yellow', 'purple', 'orange']

WEB_URL = 'https://d36mxiodymuqjm.cloudfront.net/'
cards_icon_url = WEB_URL + 'website/ui_elements/open_packs/packsv2/img_pack_chaos-legion_opt.png'
dec_icon_url = WEB_URL + 'website/icon_dec.png'
land_icon_url_svg = WEB_URL + 'website/ui_elements/popups/land_presale/img_plot.svg'
sps_icon_url = WEB_URL + 'website/ui_elements/shop/cl/img_sps-shard_128.png'
coins_icon_url = WEB_URL + 'website/ui_elements/shop/img_credits.png'
other_icon_url = WEB_URL + 'website/nav/icon_nav_items_active@2x.png'
glint_icon_url = WEB_URL + 'website/icons/icon_resource_glint.png'
voucher_icon_url = ('https://files.peakd.com/file/peakd-hive/beaker007/'
                    'Eo8RPwT4kQnGyvkNp9Vx1kLpFYYVhKSy88Fsy7YrAStKwrHCRX6GNvhywGxPbQpW2bu.png')
voucher_icon_url_svg = WEB_URL + 'website/ui_elements/shop/cl/voucher-css.svg'

merit_icon_url = WEB_URL + 'website/icons/img_merit_256.png'
energy_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/img_reward_energy_150.png'
potion_gold_icon_url = WEB_URL + 'website/ui_elements/shop/potions/potion_gold.png'
potion_legendary_icon_url = WEB_URL + 'website/ui_elements/shop/potions/potion_legendary.png'
beta_pack_icon = WEB_URL + 'website/icons/icon_pack_beta.png'
land_plot_icon_url = WEB_URL + 'website/icons/icon_claim_plot_256.png'

reward_draw_initiate_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_reward_initiate-draw_150.png'
reward_draw_adept_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_reward_adept-draw_150.png'
reward_draw_veteran_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_reward_veteran-draw_150.png'
reward_draw_elite_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_reward_elite-draw_150.png'
reward_draw_master_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_reward_master-draw_150.png'

reward_draw_common_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_draws-common_800.png'
reward_draw_rare_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_draws-rare_800.png'
reward_draw_epic_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_draws-epic_800.png'
reward_draw_legendary_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_draws-legendary_800.png'

reward_draw_minor_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_chest-minor_250.webp'
reward_draw_major_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_chest-major_250.webp'
reward_draw_ultimate_icon_url = WEB_URL + 'website/ui_elements/shop/ranked/draws/img_chest-ultimate_250.webp'

wild_league_icon_url = WEB_URL + 'website/icons/leagues/wild_150/league_0.png'
modern_league_icon_url = WEB_URL + 'website/icons/leagues/modern_150/league_0.png'

guild_icon_url = WEB_URL + 'website/nav/icon_nav_guilds_active@2x.png'
tournament_icon_url = WEB_URL + 'website/nav/icon_nav_events_active@2x.png'
battle_icon_url = WEB_URL + 'website/nav/icon_nav_battle_active@2x.png'

replay_icon_url = WEB_URL + 'website/ui_elements/icon_replay_active.svg'
trophy_icon_url = WEB_URL + 'website/ui_elements/img_monster-trophy.png'
mana_icon_url = WEB_URL + 'website/ui_elements/bg_mana.png'


class ExtendedEnum(Enum):

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))


class Format(ExtendedEnum):
    wild = 'wild'
    modern = 'modern'


class MatchType(ExtendedEnum):
    RANKED = 'Ranked'
    TOURNAMENT = 'Tournament'
    BRAWL = 'Brawl'
    CHALLENGE = 'Challenge'


class CardType(ExtendedEnum):
    summoner = 'Summoner'
    monster = 'Monster'


class Leagues(ExtendedEnum):
    NOVICE = 0
    BRONZE_III = 1
    BRONZE_II = 2
    BRONZE_I = 3
    SILVER_III = 4
    SILVER_II = 5
    SILVER_I = 6
    GOLD_III = 7
    GOLD_II = 8
    GOLD_I = 9
    DIAMOND_III = 10
    DIAMOND_II = 11
    DIAMOND_I = 12
    CHAMPION_III = 13
    CHAMPION_II = 14
    CHAMPION_I = 15


class RatingLevel(ExtendedEnum):
    Novice = 0
    Bronze = 1
    Silver = 2
    Gold = 3
    Diamond = 4
    Champion = 5


class Edition(ExtendedEnum):
    alpha = 0
    beta = 1
    promo = 2
    reward = 3
    untamed = 4
    dice = 5
    gladius = 6
    chaos = 7
    rift = 8
    soulbound = 10
    rebellion = 12


class Element(ExtendedEnum):
    water = 'Blue'
    death = 'Black'
    fire = 'Red'
    life = 'White'
    dragon = 'Gold'
    earth = 'Green'
    neutral = 'Gray'


class Rarity(ExtendedEnum):
    common = 1
    rare = 2
    epic = 3
    legendary = 4


class ManaCap(ExtendedEnum):
    low = '0-20'
    medium = '21-40'
    high = '41-60'
    max = '61-999'
