import os

import dash_bootstrap_components as dbc
from dash import html

from main import app
from src.static.static_values_enum import Element, Edition, CardType, Rarity


def get_filter_buttons(enumeration):
    buttons = []
    last_item = list(enumeration)[-1]
    first = True
    for enum in enumeration:
        if first:
            first=False
            rounding = '50% 0% 0% 50%'
        elif last_item.name == enum.name:
            rounding = '0% 50% 50% 0%'
        else:
            rounding = '0% 0% 0% 0%'



        buttons.append(dbc.Button(
            id=enum.name + '-filter-button',
            children=[
                html.Img(
                    src=app.get_asset_url(get_icon(enumeration, enum.name)),
                    className='round-sm-img',
                    style={'width': '30px',
                           'height': '30px',
                           'padding': '5px'}
                ),
            ], style={'border-radius': rounding,
                      'border-style': 'none',
                      'width': '40px',
                      'height': '40px',
                      'padding': '0px',
                      'margin-top': '3px',
                      'margin-bottom': '3px',
                      'display': 'flex',
                      'justify-content': 'center',
                      'align-items': 'center'},
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
                html.P(enum.value, style={'padding-top': '7px'}),
            ], style={'border-radius': rounding,
                      'border-style': 'none',
                      'width': '65px',
                      'height': '40px',
                      'padding': '0px',
                      'text-align': 'center'},
        ),
        )
    return buttons


def get_icon(enum, name):
    if enum == Element:
        return os.path.join("icons", 'icon-element-' + name + '-2.svg')
    elif enum == CardType:
        return os.path.join("icons", 'icon-type-' + name + '.svg')
    elif enum == Edition:
        if name == Edition.soulbound.name:
            return os.path.join("icons", 'img_overlay_' + name + '.png')
        else:
            return os.path.join("icons", 'icon-edition-' + name + '.svg')
    elif enum == Rarity:
        return os.path.join("icons", 'icon-rarity-' + name + '.svg')
