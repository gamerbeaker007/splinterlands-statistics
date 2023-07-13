import json

import pandas as pd
from dateutil import parser

from src.api import spl
from src.static.static_values_enum import RatingLevel


def get_tournaments_info(username, start_date, end_date):
    collect = pd.DataFrame()
    tournaments_ids = spl.get_player_tournaments_ids(username)
    for tournament_id in tournaments_ids:
        tournament = spl.get_tournament(tournament_id)

        if tournament['status'] == 2 and tournament['rounds'][-1]['status'] == 2:
            date_time = parser.parse(str(tournament['rounds'][-1]['start_date']))

            if parser.parse(start_date) <= date_time <= parser.parse(end_date):
                player_data = list(filter(lambda item: item['player'] == username, tournament['players']))
                # If player did not leave and is found continue
                if player_data:
                    player_data = player_data[0]

                    prize_qty = "0"
                    prize_type = ""
                    if player_data['prize']:
                        prize_qty = player_data['prize']
                    else:
                        if player_data['ext_prize_info']:
                            prize_info = json.loads(player_data['ext_prize_info'])
                            prize_qty = prize_info[0]['qty']
                            prize_type = prize_info[0]['type']

                    tournament_record = {
                        'name': tournament['name'],
                        'league': RatingLevel(tournament['data']['rating_level']).name,
                        'num_players': tournament['num_players'],
                        'finish': player_data['finish'],
                        'wins': player_data['wins'],
                        'losses': player_data['losses'],
                        'draws': player_data['draws'],
                        'entry_fee': player_data['fee_amount'],
                        'prize_qty': prize_qty,
                        'prize_type': prize_type
                    }
                    collect = pd.concat([collect, pd.DataFrame(tournament_record, index=[0])], ignore_index=True)
    return collect
