import os

import dash_bootstrap_components as dbc
from dash import html

from src.pages.main_dash import app
from src.static.static_values_enum import Element, CardType, Edition, Rarity, MatchType, Format, SPL_NEXT_URL, WEB_URL


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
    prefix = f'{WEB_URL}website/icons/'
    battle_prefix = f'{WEB_URL}website/nav/'
    ui_elements_prefix = f'{WEB_URL}website/ui_elements/'
    rarity_prefix = f'{WEB_URL}website/create_team/'
    card_prefix = f'{SPL_NEXT_URL}assets/cards/'
    icon_prefix = f'{WEB_URL}website/collection/'

    if enum == Element:
        return f'{card_prefix}icon_element_{name}_off.svg'

    elif enum == CardType:
        cardtype_map = {
            CardType.monster.name: f'{icon_prefix}icon_filter_units.svg',
            CardType.summoner.name: f'{icon_prefix}icon_filter_archons.svg'
        }
        return cardtype_map.get(name, f'{card_prefix}noattack_off.png')

    elif enum == Edition:
        if name in {Edition.soulbound.name, Edition.soulboundrb.name}:
            return app.get_asset_url(os.path.join('icons', f'img_overlay_{name}.png'))
        elif name == Edition.conclave.name:
            return f'{prefix}icon-edition-{name}-arcana.svg'
        else:
            return f'{prefix}icon-edition-{name}.svg'

    elif enum == Rarity:
        # https://d36mxiodymuqjm.cloudfront.net/website/create_team/icon_rarity_common_new.svg
        # https://d36mxiodymuqjm.cloudfront.net/website/create_team/icon_rarity_common.svg
        return f'{rarity_prefix}icon_rarity_{name}_new.svg'

    elif enum == Format:
        return f'{card_prefix}icon_format_{name}_off.svg'

    elif enum == MatchType:
        matchtype_map = {
            MatchType.CHALLENGE.name: f'{ui_elements_prefix}img_challenge-sword.png',
            MatchType.RANKED.name: f'{battle_prefix}icon_nav_battle_active@2x.png',
            MatchType.BRAWL.name: f'{battle_prefix}icon_nav_guilds_active@2x.png',
            MatchType.TOURNAMENT.name: f'{battle_prefix}icon_nav_events_active@2x.png'
        }
        return matchtype_map.get(name)

    return None  # fallback in case nothing matched
