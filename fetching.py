import os
from pickle import FALSE

import soccerdata as sd
import numpy as np
import pandas as pd
from preprocessing import prep_schedule_data


def _get_current_season():
    current_year = pd.Timestamp.today().year
    current_month = pd.Timestamp.today().month
    if current_month > 6 :
        return current_year 
    else:
        return current_year - 1 


def fetch_current_season_data(use_saved=False):
    print("Fetching new current season data")
    
    current_season = _get_current_season()
    if not use_saved:
        fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
        schedule = fbref.read_schedule()
        schedule.to_csv(os.path.join("data", "schedule.csv"), index=False)
    else: 
        schedule = pd.read_csv(os.path.join("data", "schedule.csv"), parse_dates=["date"])
    
    return schedule


def fetch_current_table_data(use_saved=False):
    print(f"Fetching new current standings data")
    
    curr_s = _get_current_season()
    
    if not use_saved:
        url = f"https://fbref.com/en/comps/20/{str(curr_s)}-{str(curr_s+1)}/{str(curr_s)}-{str(curr_s+1)}-Bundesliga-Stats"

        tables = pd.read_html(url)
        standings = tables[0]
        standings.to_csv(os.path.join("data", "standings.csv"), index=False)
        
        standings_home_away = tables[1]
        standings_home_away.to_csv(os.path.join("data", "standings_home_away.csv"), index=False)
    else:
        standings = pd.read_csv(os.path.join("data", "standings.csv"), header=[0])
        standings_home_away = pd.read_csv(os.path.join("data", "standings_home_away.csv"), header=[0,1])

    return standings, standings_home_away


def fetch_club_match_data(club_name, use_saved=False):
    print(f"Fetching new club match data for {club_name}")
    
    current_season = _get_current_season()
    
    if not use_saved:
        fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
        team_match_stats= fbref.read_team_match_stats(stat_type="schedule", team=club_name)
        team_match_stats.to_csv(os.path.join("data", f"stats_{club_name}.csv"))
    else:
        team_match_stats = pd.read_csv(os.path.join("data", f"stats_{club_name}.csv"), parse_dates=["date"])
    
    return team_match_stats

def fetch_club_season_data(use_saved=False):
    print(f"Fetching club season data")
    
    if not use_saved:
        current_season = _get_current_season()
        fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
    
        team_season_stats = fbref.read_team_season_stats()
        team_season_stats.to_csv(os.path.join("data", f"team_season_stats.csv"))
        
    else:
        team_season_stats = pd.read_csv(os.path.join("data", f"team_season_stats.csv"), header=[0,1], index_col=[0,1,2])
        fixed_column_tuples = [(colA, '') if colB.startswith("Unnamed:") else (colA, colB)  for colA, colB in team_season_stats.columns]
        team_season_stats.columns = pd.MultiIndex.from_tuples(fixed_column_tuples)
    
    return team_season_stats

    

def fetch_head_to_head_data(home_club_id, away_club_id, use_saved=False):
    print(f"Fetching club season data")
    
    if not use_saved:
        url = f"https://fbref.com/en/stathead/matchup/teams/{home_club_id}/{away_club_id}/"

        h2h_table = pd.read_html(url)[0]
        h2h_table.to_csv(os.path.join("data", f"h2h_{home_club_id}_{away_club_id}.csv"))
    else:
        h2h_table = pd.read_csv(os.path.join("data", f"h2h_{home_club_id}_{away_club_id}.csv"))
        
    return h2h_table



    
    