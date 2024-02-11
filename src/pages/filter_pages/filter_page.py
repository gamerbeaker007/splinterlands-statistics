import os

import dash_bootstrap_components as dbc
from dash import html

from src.configuration import config
from src.pages.main_dash import app
from src.static.static_values_enum import Element, CardType, Edition, Rarity, MatchType, Format


def get_filter_buttons(enumeration):
    buttons = []
    last_item = list(enumeration)[-1]
    first = True
    for enum in enumeration:
        if first:
            first = False
            rounding = '50% 0% 0% 50%'
        elif last_item.name == enum.name:
            rounding = '0% 50% 50% 0%'
        else:
            rounding = '0% 0% 0% 0%'

        buttons.append(
            dbc.Button(
                id=enum.name + '-filter-button',
                title=enum.name.title(),
                className='dbc bg-opacity-10 bg-dark',
                children=[
                    html.Img(
                        src=get_icon_url(enumeration, enum.name),
                        className='round-sm-img',
                        style={'width': '30px',
                               'height': '30px',
                               'padding': '5px'}
                    ),
                ],
                style={
                    'borderRadius': rounding,
                    'borderStyle': 'none',
                    'width': '40px',
                    'height': '40px',
                    'padding': '0px',
                    'marginTop': '3px',
                    'marginBottom': '3px',
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center'
                },
            ),
        )
    return buttons


def get_filter_buttons_text(enumeration):
    buttons = []
    last_item = list(enumeration)[-1]
    for enum in enumeration:
        if last_item.name == enum.name:
            rounding = '0% 20% 20% 0%'
        else:
            rounding = '0% 0% 0% 0%'

        buttons.append(dbc.Button(
            id=enum.name + '-filter-button',
            className='dbc bg-opacity-10 bg-dark',
            children=[
                html.P(enum.value, style={'paddingTop': '7px'}),
            ], style={
                'borderRadius': rounding,
                'borderStyle': 'none',
                'width': '65px',
                'height': '40px',
                'padding': '0px',
                'textAlign': 'center'},
        ),
        )
    return buttons


def get_icon_url(enum, name):
    # https://d36mxiodymuqjm.cloudfront.net/website/icons/icon-edition-alpha.svg
    prefix = str(config.settings['asset_url']) + 'website/icons/'
    next_prefix = 'https://next.splinterlands.com/assets/cards/'

    if enum == Element:
        # Other option https://next.splinterlands.com/assets/cards/icon_element_water_off.svg
        return next_prefix + 'icon_element_' + str(name) + '_off.svg'
    elif enum == CardType:
        # https://next.splinterlands.com/assets/cards/icon_role_units_on.svg
        if name == CardType.monster.name:
            return next_prefix + 'icon_role_units_off.svg'
        elif name == CardType.summoner.name:
            return next_prefix + 'icon_role_summoners_off.svg'
        else:
            # fallback noattack_off.png
            return next_prefix + 'noattack_off.png'
    elif enum == Edition:
        if name == Edition.soulbound.name:
            return app.get_asset_url(os.path.join('icons', 'img_overlay_' + str(name) + '.png'))
        else:
            return prefix + 'icon-edition-' + str(name) + '.svg'
    elif enum == Rarity:
        return next_prefix + str(name) + 'Off.svg'
    elif enum == Format:
        return next_prefix + 'icon_format_' + str(name) + '_off.svg'
    elif enum == MatchType:
        battle_prefix = str(config.settings['asset_url']) + 'website/nav/'
        if MatchType.CHALLENGE.name == name:
            return 'https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/img_challenge-sword.png'
        elif MatchType.RANKED.name == name:
            return battle_prefix + 'icon_nav_battle_active@2x.png'
        elif MatchType.BRAWL.name == name:
            return battle_prefix + 'icon_nav_guilds_active@2x.png'
        elif MatchType.TOURNAMENT.name == name:
            return battle_prefix + 'icon_nav_events_active@2x.png'
