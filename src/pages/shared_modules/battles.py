import json

import dash_bootstrap_components as dbc
from dash import html
from dateutil import parser

from src import analyse
from src.api import spl
from src.configuration import config
from src.static.static_values_enum import MatchType, guild_icon_url, tournament_icon_url, battle_icon_url, Format, \
    replay_icon_url, trophy_icon_url, WEB_URL, mana_icon_url


def get_mana_div(mana):
    div_style = {
        'width': '50px',
        'height': '50px',
        'position': 'relative',
    }
    img_style = {'backgroundImage': 'url(' + str(mana_icon_url) + ')',
                 'backgroundSize': '100%',
                 'height': '50px',
                 'width': '50px'}

    text_style = {
        'textAlign': 'center',
        'paddingTop': '10px'
    }

    return dbc.Col(style=div_style,
                   width=1,
                   className='m-1',
                   children=dbc.Col(style=img_style, children=html.H5(str(mana), style=text_style)))


def get_ruleset_div(rule_sets):
    prefix = WEB_URL + 'website/icons/rulesets/new/img_combat-rule_'
    suffix = '_150.png'

    ruleset_layout = []
    for ruleset in rule_sets:
        replaced = ruleset.replace(' ', '-').lower()
        replaced = replaced.replace('&-', '').lower()  # Up close & Personal
        replaced = replaced.replace('?', '-').lower()  # Are you not entertained?
        replaced = replaced.replace('’', '-').lower()  # What doesn’t kill you

        url = prefix + replaced + suffix

        img_style = {'height': '50px',
                     'width': '50px'}
        ruleset_layout.append(html.Img(src=url, title=ruleset, style=img_style, className='m-1'))

    return dbc.Col(children=ruleset_layout)


def get_replay_link(battle_id):
    link = 'https://next.splinterlands.com/battle/' + battle_id

    img_style = {'height': '40px',
                 'width': '40px'}

    return dbc.Col(className='m-1 pt-1',
                   children=html.A(title=link,
                                   href=link,
                                   target='_black',
                                   children=html.Img(src=replay_icon_url,
                                                     title='Replay',
                                                     style=img_style)))


def get_match_type_col(match_type, is_brawl):
    img_style = {'height': '40px',
                 'width': '40px'}

    if match_type == MatchType.TOURNAMENT.value:
        if is_brawl:
            match_type = MatchType.BRAWL.value
            img = guild_icon_url
        else:
            img = tournament_icon_url
    else:
        img = battle_icon_url

    return dbc.Col(className='m-1 pt-1',
                   children=html.Img(src=img,
                                     title=match_type,
                                     style=img_style))


def get_match_format(match_format):
    if match_format:
        match_format = Format.modern.value.capitalize()
    else:
        match_format = Format.wild.value.capitalize()
    return dbc.Col(match_format, className='mt-3')


def get_battle_rows(account, battle_ids):
    result_layout = []
    for battle_id in battle_ids:
        row_result = []
        battle_row = spl.get_battle(battle_id)
        battle_details = json.loads(battle_row['details'])
        if battle_details['team1']['player'] == account:
            my_team = battle_details['team1']
            opponent_team = battle_details['team2']
        else:
            my_team = battle_details['team2']
            opponent_team = battle_details['team1']

        date = parser.parse(battle_row['created_date'])
        mana = battle_row['mana_cap']
        rule_sets = battle_row['ruleset'].split('|')
        match_type = battle_row['match_type']
        match_format = battle_row['format']

        is_brawl = False
        if 'is_brawl' in battle_details:
            is_brawl = battle_details['is_brawl']
        is_win = True if battle_row['winner'] == account else False

        battle_info_row = dbc.Row(children=[dbc.Col(str(date.strftime("%Y-%m-%d %H:%M:%S")), width=2, className='mt-3'),
                                            get_mana_div(mana),
                                            get_ruleset_div(rule_sets),
                                            get_replay_link(battle_id),
                                            get_match_type_col(match_type, is_brawl),
                                            get_match_format(match_format),
                                            ])

        battle_row = dbc.Row(children=[
            dbc.Col(children=get_team(my_team, is_win), style={'display': 'flex'}),
            dbc.Col(children=get_team(opponent_team, is_win, home_team=False), style={'display': 'contents'})
        ])

        row_result.append(battle_info_row)
        row_result.append(battle_row)

        result_layout.append(
            dbc.Row(row_result, className='mb-3 p-1 border border-primary rounded bg-light text-primary'))
    return result_layout


def get_team(my_team, is_win, home_team=True):
    result = []

    summoner_style = {'height': '150px'}
    monster_style = {'height': '100px'}
    win_style = {'height': '40px',
                 'width': '40px'}

    if home_team:
        if is_win:
            result.append(html.Img(src=trophy_icon_url, style=win_style))

        card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
        url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])
        result.append(html.Img(src=url, style=summoner_style))

        for unit in reversed(my_team['monsters']):
            card_name = config.card_details_df.loc[unit['card_detail_id']]['name']
            url = analyse.get_image_url(card_name, unit['level'],
                                        unit['edition'])
            result.append(html.Img(src=url, style=monster_style))

    if not home_team:
        for unit in my_team['monsters']:
            card_name = config.card_details_df.loc[unit['card_detail_id']]['name']
            url = analyse.get_image_url(card_name, unit['level'],
                                        unit['edition'])
            result.append(html.Img(src=url, style=monster_style))

        card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
        url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])
        result.append(html.Img(src=url, style=summoner_style))

        if not is_win:
            result.append(html.Img(src=trophy_icon_url, style=win_style))

    return result
