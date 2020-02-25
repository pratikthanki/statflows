latest_game_query = 'EXEC [dbo].[sp_LatestPlayerApps]'
shot_chart_query = "EXEC [dbo].[sp_ShotChart] @PlayerId='{0}', @Period='{1}', @Venue='{2}'"
team_roster_query = '''
SELECT 
r.[teamid] 
,[season]
,[leagueid]
,[player]
,[num]
,[position]
,[height]
,[weight]
,[birth_date]
,[age]
,[exp]
,[school]
,r.[player_id]
FROM [NBA].[dbo].[rosters] r
JOIN (
    SELECT 
        [teamid]
        ,[player_id]
        ,MAX([LastUpdated]) as Latest
    FROM [NBA].[dbo].[rosters]
    WHERE [season] = 2019
    GROUP BY [teamid] ,[player_id]
) l 
    ON l.player_id = r.player_id
    AND l.teamid = r.teamid
    AND l.Latest = r.LastUpdated
'''
team_season_stats_query = 'EXEC [dbo].[sp_TeamSeasonStats]'

team_query = 'SELECT * FROM [dbo].[vwTeams]'

SHOT_PLOT_COLUMNS = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX', 'LocationY', 'Period', 'TeamID',
                     'PlayerID', 'Date', 'Season', 'Venue']

TEAM_COLUMNS = ['TeamID', 'TeamCode', 'TeamLogo', 'Division', 'Conference']

TEAM_STATS_COLUMNS = ['tid', 'teamcode', 'season', 'ast', 'games', 'blk', 'blka', 'dreb', 'fbpts', 'fbptsa',
                      'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
                      'pts', 'reb', 'stl', 'tov', 'tpa', 'tpm']

# Old columns: 'TeamLogo', 'PlayerImg', 'Division', 'Conference'
CURRENT_ROSTER_COLUMNS = ['team_id', 'Season', 'league_id', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                          'DoB', 'Age', 'Experience', 'School', 'player_id']
