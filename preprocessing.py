import os

import numpy as np
import pandas as pd


def _get_current_season():
    current_year = pd.Timestamp.today().year
    current_month = pd.Timestamp.today().month
    if current_month > 6 :
        return current_year 
    else:
        return current_year - 1 


def _club_to_abbr (club_name):
    clubs_abbr = {'Werder Bremen': "SVW",
                    'Augsburg': "FCA",
                    'Dortmund': "BVB",
                    'Hoffenheim': "TSG",
                    'Leverkusen': "B04",
                    'Stuttgart': "VfB",
                    'Wolfsburg': "WOB",
                    'Eint Frankfurt': "SGE",
                    'Union Berlin': "FCU",
                    'RB Leipzig': "RBL",
                    'Bochum': "BOC",
                    'Darmstadt 98': "SVD",
                    'Freiburg': "SCF",
                    'Heidenheim': "HDH",
                    'Köln': "KOE",
                    "M'Gladbach": "BMG",
                    'Bayern Munich': "FCB",
                    'Mainz 05': "M05"}
    if club_name in clubs_abbr:
        return clubs_abbr[club_name]
    else: 
        return club_name[:3].upper()


def prep_schedule_data(schedule: pd.DataFrame):
    
    
    current_season = _get_current_season()
    
    schedule_mod = (schedule
        .assign(datetime=lambda df:df["date"].dt.strftime('%Y-%m-%d') + " " + df["time"], 
                datetime_ts=lambda df: pd.to_datetime(df["datetime"]),
                today= pd.Timestamp.today(),
                time_to_start=lambda df: df["datetime_ts"] - df["today"],
                time_to_start_days=lambda df: df["time_to_start"].dt.days,
                time_to_start_hours=lambda df: df["time_to_start"].dt.seconds // (60*60),
                home_abbr=lambda df: df["home_team"].map(_club_to_abbr), 
                away_abbr=lambda df: df["away_team"].map(_club_to_abbr),
                game_str=lambda df: df["home_abbr"] +  " vs " + df["away_abbr"])
        .drop(columns=["datetime", "today"])
    )
    return schedule_mod



def prep_current_table_data(standings, standings_home_away):
    keep = ['Rk', 'Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'Pts/MP',
        'xG', 'xGA', 'xGD', 'xGD/90', 'Last 5']
    
    home_cols = [(l1, l2) for l1, l2 in standings_home_away.columns if l1 != "Away"]
    away_cols = [(l1, l2) for l1, l2 in standings_home_away.columns if l1 != "Home"]
    home_table = (standings_home_away[home_cols]
                        .droplevel(0, axis=1)
                        .sort_values(by="Pts", ascending=False)
                        .reset_index(drop=True)
                        .reset_index()
                        .assign(home_rk=lambda df: df["index"] + 1)
                        .drop(columns=["index"]))
    
    
    away_table = (standings_home_away[away_cols]
                        .droplevel(0, axis=1)
                        .sort_values(by="Pts", ascending=False)
                        .reset_index(drop=True)
                        .reset_index()
                        .assign(away_rk=lambda df: df["index"] + 1)
                        .drop(columns=["index"]))
    return standings[keep], home_table, away_table



def prep_club_match_data(team_match_stats):
    keep = ["game", "date", 'round', 'day', 'venue', 'result', 'GF', 'GA',
       'opponent', 'xG', 'xGA', 'Poss']
    team_match_stats_agg = (team_match_stats
                                .query("not match_report.isna()")
                                .tail(5)
                                .reset_index())[keep]
    
    return team_match_stats_agg



def prep_club_season_data(team_season_stats):
    team_season_stats_prep = (team_season_stats
                                .assign(team_id=lambda df: df[("url", "")].str.split("/").str[3])
                                .reset_index()
                                .drop(columns=["league", "season", "url"], level=0))
    
    return team_season_stats_prep

    

def prep_head_to_head_data(h2h_table):
    
    
    keep = ['Comp', 'Round', 'Date', 'Home', 'xG', 'Score', 'xG.1', 'Away']
    h2h_table = (h2h_table
                    .query("not Score.isnull() and Score != 'Score'")
                    .assign(dt=lambda df: pd.to_datetime(df["Date"]).dt.year, 
                            year_diff=lambda df: df["dt"].max() - df["dt"])
                    .query("year_diff < 5"))[keep]
    
    return h2h_table



