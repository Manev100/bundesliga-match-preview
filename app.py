import streamlit as st
import streamlit.components.v1 as components
import soccerdata as sd
import numpy as np
import pandas as pd

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
    print("Fetching new current season data")
    
    
    def club_to_abbr (club_name):
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
    
    
    current_season = get_current_season()
    fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
    schedule = fbref.read_schedule()
    schedule_mod = (schedule
        .assign(datetime=lambda df:df["date"].dt.strftime('%Y-%m-%d') + " " + df["time"], 
                datetime_ts=lambda df: pd.to_datetime(df["datetime"]),
                today= pd.Timestamp.today(),
                time_to_start=lambda df: df["datetime_ts"] - df["today"],
                time_to_start_days=lambda df: df["time_to_start"].dt.days,
                time_to_start_hours=lambda df: df["time_to_start"].dt.seconds // (60*60),
                home_abbr=lambda df: df["home_team"].map(club_to_abbr), 
                away_abbr=lambda df: df["away_team"].map(club_to_abbr),
                game_str=lambda df: df["home_abbr"] +  " vs " + df["away_abbr"])
        .drop(columns=["datetime", "today"])
    )
    return schedule_mod


def reset_current_season_data ():
    get_current_season_data.clear()


@st.cache_data
def get_current_table_data():
    curr_s = get_current_season()
    url = f"https://fbref.com/en/comps/20/{str(curr_s)}-{str(curr_s+1)}/{str(curr_s)}-{str(curr_s+1)}-Bundesliga-Stats"

    tables = pd.read_html(url)
    standings = tables[0]

    keep = ['Rk', 'Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'Pts/MP',
        'xG', 'xGA', 'xGD', 'xGD/90', 'Last 5']
    
    home_cols = [(l1, l2) for l1, l2 in tables[1].columns if l1 != "Away"]
    away_cols = [(l1, l2) for l1, l2 in tables[1].columns if l1 != "Home"]
    home_table = (tables[1][home_cols]
                        .droplevel(0, axis=1)
                        .sort_values(by="Pts", ascending=False)
                        .reset_index(drop=True)
                        .reset_index()
                        .assign(home_rk=lambda df: df["index"] + 1)
                        .drop(columns=["index"]))
    
    
    away_table = (tables[1][away_cols]
                        .droplevel(0, axis=1)
                        .sort_values(by="Pts", ascending=False)
                        .reset_index(drop=True)
                        .reset_index()
                        .assign(away_rk=lambda df: df["index"] + 1)
                        .drop(columns=["index"]))
    return standings[keep], home_table, away_table

def reset_current_table_data ():
    get_current_table_data.clear()


@st.cache_data
def get_club_match_data(club_name):
    print(f"Fetching new club match data for {club_name}")
    
    current_season = get_current_season()
    fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
    
    team_match_stats= fbref.read_team_match_stats(stat_type="schedule", team=club_name)
    
    keep = ["game", "date", 'round', 'day', 'venue', 'result', 'GF', 'GA',
       'opponent', 'xG', 'xGA', 'Poss']
    team_match_stats_agg = (team_match_stats
                                .query("not match_report.isna()")
                                .tail(5)
                                .reset_index())[keep]
    
    return team_match_stats_agg

def reset_club_match_data ():
    get_club_match_data.clear()

@st.cache_data
def get_club_season_data():
    print(f"Fetching club season data")
    
    current_season = get_current_season()
    fbref = sd.FBref(leagues="GER-Bundesliga", seasons=str(current_season)[2:])
    
    team_season_stats = (fbref.read_team_season_stats()
                                .assign(team_id=lambda df: df[("url", "")].str.split("/").str[3])
                                .reset_index()
                                .drop(columns=["league", "season", "url"]))
    
    
    return team_season_stats

def reset_club_season_data ():
    get_club_season_data.clear()
    

@st.cache_data
def get_head_to_head_data(home_club_id, away_club_id):
    print(f"Fetching club season data")
    
    curr_s = get_current_season()
    url = f"https://fbref.com/en/stathead/matchup/teams/{home_club_id}/{away_club_id}/"

    h2h_tables = pd.read_html(url)
    
    keep = ['Comp', 'Round', 'Date', 'Home', 'xG', 'Score', 'xG.1', 'Away']
    h2h_table = (h2h_tables[0]
                    .query("not Score.isnull() and Score != 'Score'")
                    .assign(dt=lambda df: pd.to_datetime(df["Date"]).dt.year, 
                            year_diff=lambda df: df["dt"].max() - df["dt"])
                    .query("year_diff < 5"))[keep]
    
    return h2h_table


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
    
    