import os

import dash_bootstrap_components as dbc
from dash import html

from main import app
from src.configuration import config
from src.pages.filter_pages import filter_style
from src.static.static_values_enum import Element, CardType, Edition, Rarity


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

        buttons.append(dbc.Button(
            id=enum.name + '-filter-button',
            children=[
                html.Img(
                    src=get_icon_url(enumeration, enum.name),
                    className='round-sm-img',
                    style={'width': '30px',
                           'height': '30px',
                           'padding': '5px'}
                ),
            ], style={
                'backgroundColor': filter_style.btn_inactive_color,
                'borderRadius': rounding,
                'borderStyle': 'none',
                'width': '40px',
                'height': '40px',
                'padding': '0px',
                'marginTop': '3px',
                'marginBottom': '3px',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'},
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
            children=[
                html.P(enum.value, style={'paddingTop': '7px'}),
            ], style={
                'backgroundColor': filter_style.btn_inactive_color,
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

    if enum == Element:
        return prefix + 'icon-element-' + str(name) + '-2.svg'
    elif enum == CardType:
        return prefix + 'icon-type-' + str(name) + '.svg'
    elif enum == Edition:
        if name == Edition.soulbound.name:
            return app.get_asset_url(os.path.join('icons', 'img_overlay_' + str(name) + '.png'))
        else:
            return prefix + 'icon-edition-' + str(name) + '.svg'
    elif enum == Rarity:
        return prefix + 'icon-rarity-' + str(name) + '.svg'
