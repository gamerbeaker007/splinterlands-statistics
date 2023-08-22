import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Output, Input, html
from dash.exceptions import PreventUpdate
from dateutil import parser

from main import app
from src import analyse
from src.api import spl
from src.configuration import config
from src.pages.nemesis_pages import nemesis_page_ids

layout = dbc.Row(id=nemesis_page_ids.opponent_battles)


def get_mana_div(mana):
    url = 'https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/bg_mana.png'
    div_style = {
        'width': '50px',
        'height': '50px',
        'position': 'relative',
    }
    img_style = {'background-image': 'url(' + str(url) + ')',
                 'background-size': '100%',
                 'height': '50px',
                 'width': '50px'}

    text_style = {
        'text-align': 'center',
        'padding-top': '10px'
    }

    return dbc.Col(style=div_style,
                   width=1,
                   className='m-1',
                   children=dbc.Col(style=img_style, children=html.H5(str(mana), style=text_style)))


def get_ruleset_div(rule_sets):
    prefix = 'https://d36mxiodymuqjm.cloudfront.net/website/icons/rulesets/new/img_combat-rule_'
    suffix = '_150.png'

    ruleset_layout = []
    for ruleset in rule_sets:
        replaced = ruleset.replace(' ', '-').lower()
        replaced = replaced.replace('&-', '').lower()  # Up close & Personal
        replaced = replaced.replace('?', '-').lower()  # Are you not entertained?

        url = prefix + replaced + suffix

        img_style = {'height': '50px',
                     'width': '50px'}
        ruleset_layout.append(html.Img(src=url, title=ruleset, style=img_style, className='m-1'))

    return dbc.Col(children=ruleset_layout)


def get_replay_link(battle_id):
    link = 'https://splinterlands.com/?p=battle&id=' + battle_id
    img = 'https://d36mxiodymuqjm.cloudfront.net/website/ui_elements/icon_replay_active.svg'
    img_style = {'height': '40px',
                 'width': '40px'}
    return dbc.Col(className='m-1 pt-1',
                   children=html.A(title=link,
                                   href=link,
                                   target='_black',
                                   children=html.Img(src=img,
                                                     title='Replay',
                                                     style=img_style)))


@app.callback(
    Output(nemesis_page_ids.opponent_battles, 'children'),
    Input(nemesis_page_ids.filtered_against_df, 'data'),
)
def update_battles(filtered_df):
    if not filtered_df:
        raise PreventUpdate
    result_layout = []

    filtered_df = pd.read_json(filtered_df, orient='split')
    if not filtered_df.empty:
        last_battles = filtered_df.sort_values(by='created_date').head(5).battle_id.tolist()
        for battle_id in last_battles:
            row_result = []
            battle_row = spl.get_battle(battle_id)
            battle_details = json.loads(battle_row['details'])
            if battle_details['team1']['player'] == filtered_df.account.tolist()[0]:
                my_team = battle_details['team1']
                opponent_team = battle_details['team2']
            else:
                my_team = battle_details['team2']
                opponent_team = battle_details['team1']

            date = parser.parse(battle_row['created_date'])
            mana = battle_row['mana_cap']
            rule_sets = battle_row['ruleset'].split('|')
            battle_info_row = dbc.Row(children=[dbc.Col(str(date.date()), width=2),
                                                get_mana_div(mana),
                                                get_ruleset_div(rule_sets),
                                                get_replay_link(battle_id)
                                                ])

            battle_row = dbc.Row(children=[
                dbc.Col(children=get_team(my_team), style={'display': 'flex'}),
                dbc.Col(children=get_team(opponent_team, home_team=False), style={'display': 'contents'})
            ])

            row_result.append(battle_info_row)
            row_result.append(battle_row)

            result_layout.append(dbc.Row(row_result, className='mb-3 p-1 border border-primary rounded bg-light text-primary'))

    return result_layout


def get_team(my_team, home_team=True):
    result = []

    if home_team:
        card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
        url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])
        result.append(html.Img(src=url, style={'height': '150px'}))

    for unit in my_team['monsters']:
        card_name = config.card_details_df.loc[unit['card_detail_id']]['name']
        url = analyse.get_image_url(card_name, unit['level'],
                                    unit['edition'])

        result.append(html.Img(src=url, style={'height': '100px'}))

    if not home_team:
        card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
        url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])

        result.append(html.Img(src=url, style={'height': '150px'}))

    return result
