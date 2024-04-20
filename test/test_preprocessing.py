import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import numpy as np
import pandas as pd

from fetching import fetch_current_season_data, fetch_current_table_data, fetch_club_match_data, fetch_club_season_data, fetch_head_to_head_data
from preprocessing import prep_schedule_data, prep_current_table_data, prep_club_match_data, prep_club_season_data, prep_head_to_head_data



def test_prep_schedule_data():
    schedule = fetch_current_season_data(use_saved=True)
    schedule_prep = prep_schedule_data(schedule)
    print(schedule_prep)
    
def test_prep_current_table_data():
    standings, standings_home_away = fetch_current_table_data(use_saved=False)
    standings, home, away = prep_current_table_data(standings, standings_home_away)
    print("Standings")
    print(standings)
    print("Home")
    print(home)
    print("Away")
    print(away)
    
def test_prep_club_match_data():
    match_data = fetch_club_match_data("Bayern Munich", use_saved=True)
    match_data_prep = prep_club_match_data(match_data)
    print(match_data_prep)

def test_prep_club_season_data():
    club_season_data = fetch_club_season_data( use_saved=True)
    club_season_data_prep = prep_club_season_data(club_season_data)
    print(club_season_data_prep)


def test_prep_head_to_head_data():
    club_season_data = fetch_head_to_head_data("054efa67", "add600ae",  use_saved=True)
    print(club_season_data)
    club_season_data_prep = prep_head_to_head_data(club_season_data)
    print(club_season_data_prep)

test_prep_current_table_data()