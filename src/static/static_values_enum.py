from enum import Enum


class Format(Enum):
    MODERN = "modern"
    WILD = "wild"


class Leagues(Enum):
    NOVICE = 0
    BRONZE_III = 1
    BRONZE_II = 2
    BRONZE_I = 3
    SILVER_III = 4
    SILVER_II = 5
    SILVER_I = 6
    GOLD_III = 7
    GOLD_II = 8
    GOLD_I = 9
    DIAMOND_III = 10
    DIAMOND_II = 11
    DIAMOND_I = 12
    CHAMPION_III = 13
    CHAMPION_II = 14
    CHAMPION_I = 15


class RatingLevel(Enum):
  Novice = 0
  Bronze = 1
  Silver =2
  Gold = 3
  Diamond = 4
  Champion = 5


class Edition(Enum):
    alpha = 0
    beta = 1
    promo = 2
    reward = 3
    untamed = 4
    dice = 5
    chaos = 7
    rift = 8
    soulbound = 10


