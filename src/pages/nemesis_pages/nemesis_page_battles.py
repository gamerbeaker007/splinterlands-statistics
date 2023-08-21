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
            battle_info_row = dbc.Row(children=[dbc.Col(str(date.date()), width=2),
                                                dbc.Col(html.P("MANA")),
                                                dbc.Col(html.P("Ruleset")),
                                                dbc.Col(html.P("REPLAY"))
                                                ])

            battle_row = dbc.Row(children=[
                dbc.Col(children=get_team(my_team), style={'display': 'flex'}),
                dbc.Col(children=get_team(opponent_team, home_team=False), style={'display': 'contents'})
            ])

            row_result.append(battle_info_row)
            row_result.append(battle_row)

            result_layout.append(dbc.Row(row_result))

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

# def get_team(my_team, home_team=True):
#     result = []
#
#     if home_team:
#         card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
#         url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])
#
#         div_style = {
#             'width': '100px',
#             'height': '100px',
#             'position': 'relative',
#         }
#         img_style = {'background-image': 'url(' + str(url) + ')',
#                      'background-position': 'center 15%',
#                      'background-size': '170%',
#                      'border-radius': '50%',
#                      'color': 'rgba(0,0,0,0)',
#                      'display': 'block',
#                      'height': '100px',
#                      'object-fit': 'cover',
#                      'overflow': 'hidden',
#                      'width': '100px'}
#
#         result.append(html.Div(style=div_style,
#                                children=html.Span('test', style=img_style)
#                                )
#                       )
#
#     for unit in my_team['monsters']:
#         card_name = config.card_details_df.loc[unit['card_detail_id']]['name']
#         url = analyse.get_image_url(card_name, unit['level'],
#                                     unit['edition'])
#
#         div_style = {
#             'width': '64px',
#             'height': '64px',
#             'position': 'relative',
#         }
#         img_style = {'background-image': 'url(' + str(url) + ')',
#                      'background-position': 'center 15%',
#                      'background-size': '170%',
#                      'border-radius': '50%',
#                      'color': 'rgba(0,0,0,0)',
#                      'display': 'block',
#                      'height': '64px',
#                      'object-fit': 'cover',
#                      'overflow': 'hidden',
#                      'width': '64px'}
#
#         result.append(html.Div(style=div_style,
#                                children=html.Span('test', style=img_style)
#                                )
#                       )
#
#     if not home_team:
#         card_name = config.card_details_df.loc[my_team['summoner']['card_detail_id']]['name']
#         url = analyse.get_image_url(card_name, my_team['summoner']['level'], my_team['summoner']['edition'])
#
#         div_style = {
#             'width': '100px',
#             'height': '100px',
#             'position': 'relative',
#         }
#         img_style = {'background-image': 'url(' + str(url) + ')',
#                      'background-position': 'center 15%',
#                      'background-size': '170%',
#                      'border-radius': '50%',
#                      'color': 'rgba(0,0,0,0)',
#                      'display': 'block',
#                      'height': '100px',
#                      'object-fit': 'cover',
#                      'overflow': 'hidden',
#                      'width': '100px'}
#
#         result.append(html.Div(style=div_style,
#                                children=html.Span('test', style=img_style)
#                                )
#                       )
#
#     return result
