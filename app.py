import streamlit as st
import streamlit.components.v1 as components
import soccerdata as sd
import numpy as np
import pandas as pd

from fetching import fetch_current_season_data, fetch_current_table_data, fetch_club_match_data, fetch_club_season_data, fetch_head_to_head_data
from preprocessing import prep_schedule_data, prep_current_table_data, prep_club_match_data, prep_club_season_data, prep_head_to_head_data


st.set_page_config(
    page_title='Bundesliga Match Preview',
    page_icon='⚽',
    layout="wide"
)

st.title('Bundesliga Match Preview')
st.write("Choose upcoming match for preview")

def get_current_season():
    current_year = pd.Timestamp.today().year
    current_month = pd.Timestamp.today().month
    if current_month > 6 :
        return current_year 
    else:
        return current_year - 1 

@st.cache_data
def get_current_season_data():
    schedule = fetch_current_season_data()
    schedule_prep = prep_schedule_data(schedule)
    return schedule_prep


def reset_current_season_data ():
    get_current_season_data.clear()


@st.cache_data
def get_current_table_data():
    standings, standings_home_away = fetch_current_table_data()
    standings, home, away = prep_current_table_data(standings, standings_home_away)
    return standings, home, away

def reset_current_table_data ():
    get_current_table_data.clear()


@st.cache_data
def get_club_match_data(club_name):
    match_data = fetch_club_match_data(club_name)
    match_data_prep = prep_club_match_data(match_data)
    return match_data_prep

def reset_club_match_data ():
    get_club_match_data.clear()

@st.cache_data
def get_club_season_data():
    club_season_data = fetch_club_season_data()
    club_season_data_prep = prep_club_season_data(club_season_data)
    return club_season_data_prep

def reset_club_season_data ():
    get_club_season_data.clear()
    

@st.cache_data
def get_head_to_head_data(home_club_id, away_club_id):
    club_season_data = fetch_head_to_head_data(home_club_id, away_club_id)
    club_season_data_prep = prep_head_to_head_data(club_season_data)
    return club_season_data_prep


st.button("Reset season", type="primary", on_click=reset_current_season_data)
st.button("Reset table", type="primary", on_click=reset_current_table_data)
st.button("Reset club matches", type="primary", on_click=reset_club_match_data)
st.button("Reset club season stats", type="primary", on_click=reset_club_season_data)

current_season_data = get_current_season_data()
current_team_season_data = get_club_season_data()
team_id_df = current_team_season_data[["team", "team_id"]].droplevel(1, axis=1)
current_table_data, home_table, away_table = get_current_table_data()
current_ranks = current_table_data[["Rk", "Squad"]]


future_games = current_season_data.query("time_to_start.dt.total_seconds() > 0")

open_match_days = list(future_games["week"].unique())
open_match_days.sort()

option = st.selectbox(
    'Match Day',
    tuple(open_match_days))

query_matchday = int(option)
future_games_matchday = future_games.query("week == @query_matchday").sort_values(by="datetime_ts").reset_index()
st.write(future_games_matchday[["game", "day", "time", "time_to_start"]])

future_games_matchday["game_str"].to_list()

game_labels = future_games_matchday["game_str"].to_list()
tabs = st.tabs(game_labels)

for idx, tab_comp in enumerate(tabs):
    game_label = game_labels[idx]
    match = future_games_matchday.query("game_str == @game_label")
    home_team = match["home_team"].iloc[0]
    away_team = match["away_team"].iloc[0]

    # tab_comp.write(future_games_matchday.query("game_str == @game_label"))
    
    tab_comp.header("Table")
    
    def custom_background_style(row):
        color = 'white'
        if row["result"] == 'W':
            color = 'green'
        elif row["result"] == 'L':
            color = 'red'
        elif row["result"] == 'D':
            color = 'yellow'    

        return ['background-color: %s' % color]*len(row.values)
    
    def custom_foreground_style(row):
        color = 'white'
        if row["result"] == 'W':
            color = 'green'
        elif row["result"] == 'L':
            color = 'red'
        elif row["result"] == 'D':
            color = 'blue'    

        return ['color: %s' % color]*len(row.values)

    column_desc = {'Rk': "Rank", 'Squad': "Club", 'MP': "Matches played", 'W': "wins", 'D': "Draws", 'L': "Losses", 
    'GF': "Goals for", 'GA': "Goals agains", 'GD': "Goal difference", 'Pts': "Points", 'Pts/MP': "Points per Match Played",
        'xG': "Expected Goals - xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted)", 
        'xGA': "Expected Goals Allowed - xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted)", 
        'xGD': "Expected Goals Difference - xG totals include penalty kicks, but do not include penalty shootouts (unless otherwise noted)", 
        'xGD/90': "Expected Goals Difference per 90 Minutes", 'Last 5': "Results of last five games"}
    
    # st.dataframe(current_table_data.style.apply(custom_style, axis=1))
    print(current_table_data.columns)
    tab_comp.dataframe(current_table_data.query("(Squad == @home_team) or (Squad == @away_team)"),
                       column_config={
                           
                            name: st.column_config.Column(
                                help=desc,
                            )
                            for name, desc in  column_desc.items()
                        },
                        hide_index=True)                                    
    
    tab_comp.write(f"{home_team} home table stats")
    tab_comp.dataframe(home_table.query("(Squad == @home_team)"),
                        hide_index=True)  
    
    
    tab_comp.write(f"{away_team} away table stats")
    tab_comp.dataframe(away_table.query("(Squad == @away_team)"),
                        hide_index=True)  
        
    tab_comp.header("5 Game Form")
    
    tab_comp.write(home_team)
    team_match_stats = get_club_match_data(home_team)
    team_match_stats = team_match_stats.merge(current_ranks, how="left", left_on="opponent", right_on="Squad").drop(columns=["Squad"])
    tab_comp.dataframe(team_match_stats.style.apply(custom_foreground_style, axis=1).format({"xG": "{:.1f}", "xGA": "{:.1f}"}))
    
    tab_comp.write(away_team)
    team_match_stats = get_club_match_data(away_team)
    team_match_stats = team_match_stats.merge(current_ranks, how="left", left_on="opponent", right_on="Squad").drop(columns=["Squad"])
    tab_comp.dataframe(team_match_stats.style.apply(custom_foreground_style, axis=1).format({"xG": "{:.1f}", "xGA": "{:.1f}"}))
    
    
    tab_comp.header("Head-to-head Statistics")
    home_id = team_id_df.query(f"team == @home_team")["team_id"].iloc[0]
    away_id = team_id_df.query(f"team == @away_team")["team_id"].iloc[0]
    h2h = get_head_to_head_data(home_id, away_id)
    
    tab_comp.dataframe(h2h)
    
    tab_comp.header("Injuries")
    
    # Not very useful
    tab_comp.header("Team Season Stats")
    tab_comp.dataframe(current_team_season_data.drop(columns=["team_id"]).query("@current_team_season_data.team in [@home_team, @away_team]"))
    
    