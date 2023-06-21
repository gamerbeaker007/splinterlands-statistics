import os

import dash_bootstrap_components as dbc
from dash import html

from main import app
from src.static.static_values_enum import Element, Edition, CardType, Rarity


def get_filter_buttons(enumeration):
    buttons = []
    for enum in enumeration:
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
            ], style={'border-radius': '50%',
                      'width': '40px',
                      'height': '40px',
                      'font-size': '16px',
                      'padding': '0px',
                      'margin': '3px',
                      'display': 'flex',
                      'justify-content': 'center',
                      'align-items': 'center'},
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
