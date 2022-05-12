from requests import session
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#NHL shot analytics medium articles tutorial (for next time) : https://towardsdatascience.com/nhl-analytics-with-python-6390c5d3206d

st.title('NHL Stat Tracker')

st.write("Regular season statistics of NHL skaters from the last decade.")

selected_year = st.selectbox('Year', list(reversed(range(2012,2023)))) #Shows statistics of the last decade

# Web scraping of NHL player stats
def load_data(year):
    url = "https://www.hockey-reference.com/leagues/NHL_"+str(year)+"_skaters.html"
    #read url link for table and use header as second row
    df = pd.read_html(url, header = 1)
    df = df[0]
    # delete repeated column headers
    raw = df.drop(df[df.Age == 'Age'].index) 
    # Clean Data
    playerstats = raw.drop(['Rk', 'PS', 'EV', 'PP', 'SH', 'GW', 'EV.1', 'PP.1', 'SH.1', 'S', 'TOI', 'FOW', 'FOL', 'FO%', 'PIM', 'ATOI', 'S%', 'BLK', 'HIT'], axis=1)

    #change positions of RW, LW, and C to F
    playerstats['Pos'] = playerstats['Pos'].replace(['LW','C','RW'],'F')

    return playerstats

playerstats = load_data(selected_year)

#Expand to Filter Stats with Team and Position
filter_and_search_expander = st.expander(label='Filter Statistics')
with filter_and_search_expander:

    #Player Search
    player_name = st.text_input('Search Player', " ")
    playerstats = playerstats.loc[playerstats['Player'].str.contains(player_name, case=False)]
    st.caption('Find the statistics of a specific player using the search function. To no longer use the search function, leave the text area blank.')

    unique_pos = ['F','D']
    selected_pos = st.multiselect('Position', unique_pos, unique_pos)
    st.caption('Filter players by position: Fowards, Defencemen')
    
    #Team selection
    sorted_unique_team = sorted(playerstats.Tm.unique()) #list of unique team names from playerstats dataframe

    #Select all teams
    container = st.container()
    all = st.checkbox("Select all Teams")
 
    if all:
        selected_team = st.multiselect('Team',sorted_unique_team, sorted_unique_team)
    else:
        selected_team = st.multiselect('Team', sorted_unique_team)
    
    st.caption('Filter players by NHL teams. To statistics of all players, check the Select all Teams checkbox.')
    
    # Filtering data
    if st.button('Search'):
        playerstats = playerstats[(playerstats.Tm.isin(selected_team)) & (playerstats.Pos.isin(selected_pos))]
    st.caption('***Remember to click on the Search button to refresh the statistics with the updated filters.')

#Convert dataframe columns to correspionding data type
playerstats['PTS'] = playerstats['PTS'].astype(str).astype(int)
playerstats['G'] = playerstats['G'].astype(str).astype(int)
playerstats['A'] = playerstats['A'].astype(str).astype(int)
playerstats['+/-'] = playerstats['+/-'].astype(str).astype(int)
playerstats = playerstats.sort_values(by=['PTS','G','A','+/-'], ascending=False)

#Stat Columns Points, Goals, Assists, +/-
col1, col2, col3, col4 = st.columns(4)

#TRY TO ADD NAME OF SECOND PLACE PLAYER 

#Points Leaders 
most_points = playerstats.sort_values(by=['PTS'], ascending=False)
col1.subheader("Points")
col1.metric(most_points.iloc[0,0], most_points.iloc[0,7], (most_points.iloc[0,7]-most_points.iloc[1,7]).astype(str))

#Goal Leaders
most_goals = playerstats.sort_values(by=['G'], ascending=False)
col2.subheader("Goals")
col2.metric(most_goals.iloc[0,0], most_goals.iloc[0,5], (most_goals.iloc[0,5]-most_goals.iloc[1,5]).astype(str))

#Assist Leaders
most_assists = playerstats.sort_values(by=['A'], ascending=False)
col3.subheader("Assists")
col3.metric(most_assists.iloc[0,0], most_assists.iloc[0,6], (most_assists.iloc[0,6]-most_assists.iloc[1,6]).astype(str))

#+/- Leaders
plus_minus = playerstats.sort_values(by=['+/-'], ascending=False)
col4.subheader("+ / -")
col4.metric(plus_minus.iloc[0,0], plus_minus.iloc[0,8], (plus_minus.iloc[0,8]-plus_minus.iloc[1,8]).astype(str))

#Expand Stats Tables to show different data frames depending on specific stats
table_expander = st.expander(label='Expand Table')
with table_expander:
    option = st.selectbox(
     'Choose table to View',
     ('All', 'Points', 'Goals', 'Assists', '+/-'))

    if option == 'All':
        st.caption('Table sorted by: Points, Goals, Assists, +/-')
        playerstats
    
    elif option == 'Points':
        st.caption('Table sorted by: Points')
        most_points

    elif option == 'Goals':
        st.caption('Table sorted by: Goals')
        most_goals

    elif option == 'Assists':
        st.caption('Table sorted by: Assists')
        most_assists

    elif option == '+/-':
        st.caption('Table sorted by: +/-')
        plus_minus



#Show Season Analytics and Correlations
st.header('Advanced Analytics')

# team_selected_year = st.selectbox('Year', list(reversed(range(2013,2023)))) #Shows statistics of the last decade

team_selected_year = st.selectbox('Year', ('2022','2020','2019','2018','2017','2016','2015','2014','2013')) #Shows team stats of last decade

# Web scraping of NHL player stats
def load_data(team_year):
    url = "https://www.hockey-reference.com/leagues/NHL_"+str(team_selected_year)+".html#stats"

    df_team = pd.read_html(url, header=0)
    #Combine tables of both Eastern and Western Conference
    df_eastern = df_team[0]
    df_western = df_team[1]
    frames = [df_eastern, df_western]
    teamstats  = pd.concat(frames)

    #Perform Data Cleaning
    teams_df = teamstats.drop(['OL', 'PTS%', 'SRS', 'SOS', 'RPt%', 'RgRec', 'RgPt%'], axis=1)
    # delete repeated column headers
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'Atlantic Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'Metropolitan Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'Pacific Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'Central Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'East Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'North Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'West Division'].index) 
    teams_df = teams_df.drop(teams_df[teams_df.GP == 'Northeast Division'].index) 
    teams_df.rename(columns={'Unnamed: 0':'Team'}, inplace = True)

    teams_df['GF'] = teams_df['GF'].astype(str).astype(int)
    teams_df['GA'] = teams_df['GA'].astype(str).astype(int)
    teams_df['GP'] = teams_df['GP'].astype(str).astype(int)
    teams_df['PTS'] = teams_df['PTS'].astype(str).astype(int)

    #Add average goals for/against per game columns for each team
    teams_df['GF/G'] = teams_df['GF']/teams_df['GP']
    teams_df['GA/G'] = teams_df['GA']/teams_df['GP']
    teams_df = teams_df.round(decimals=2)

    #Add Ranking column for placing teams in each quarter of standings
    teams_df['Ranking'] = pd.Series(dtype='string')
    teams_df = teams_df.sort_values(by=['PTS'], ascending=False)
    teams_df = teams_df.reset_index(drop=True)

    for i in range(teams_df.shape[0]):
        if (i<8):
            teams_df.Ranking[i] = '1-8'

        if (i>=8 and i<16):
            teams_df.Ranking[i] = '9-16'

        if (i>=16 and i<24):
            teams_df.Ranking[i] = '17-24'

        if (i>=24 and i<33):
            teams_df.Ranking[i] = '24-32'

    return teams_df

teams_df = load_data(team_selected_year)

#Expand Stats Tables to show different data frames depending on specific stats
table_expander = st.expander(label='See Analytics')
with table_expander:

    teams_df

    sns.set_context("talk", font_scale=1.1)
    gf_vs_ga = plt.figure(figsize=(8,6))
    sns.scatterplot(x="GF/G", y="GA/G", hue="Ranking", data=teams_df)
    plt.xlabel("Goals For Per Game")
    plt.ylabel("Goals Against Per Game")
    plt.title("Average Goals For Per Game vs. Average Goals Against Per Game")

    st.pyplot(gf_vs_ga)


    #Points vs. Average Goals For Per Game
    sns.set_context("talk", font_scale=1.1)
    p_vs_gf = plt.figure(figsize=(8,6))
    sns.scatterplot(x="PTS", y="GF/G", data=teams_df, color=['green'])
    plt.xlabel("Points")
    plt.ylabel("Goals For Per Game")
    plt.title("Points vs. Average Goals For Per Game")

    st.pyplot(p_vs_gf)


    #Points vs. Average Goals Against Per Game
    sns.set_context("talk", font_scale=1.1)
    p_vs_ga = plt.figure(figsize=(8,6))
    sns.scatterplot(x="PTS", y="GA/G", data=teams_df, color=['red'])
    plt.xlabel("Points")
    plt.ylabel("Goals Against Per Game")
    plt.title("Points vs. Average Goals Against Per Game")

    st.pyplot(p_vs_ga)



    



 
