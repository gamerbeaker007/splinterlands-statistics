from src.configuration import store
from src.utils import store_util
from dateutil import parser


def get_season_played():
    season_played = store_util.get_seasons_played_list()
    return season_played


def first_played_season():
    season_played = store_util.get_seasons_played_list()
    first_season = ''
    if len(season_played) > 0:
        first_season = season_played[-1]
    return first_season


def get_season_end_date(season_id):
    season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
    from_date = parser.parse(season_end_date)
    return from_date
