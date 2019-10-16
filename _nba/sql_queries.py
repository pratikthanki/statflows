latest_game_query = 'EXEC [dbo].[sp_LatestPlayerApps]'
team_roster_query = 'EXEC [dbo].[sp_TeamRosters]'
team_query = 'SELECT * FROM [dbo].[vwTeams]'
shot_chart_query = 'EXEC [dbo].[sp_PlayerShotChart]'
standings_query = 'SELECT * FROM [dbo].[vwStandings]'
team_game_stats_query = 'EXEC [dbo].[sp_TeamGameStats]'
team_season_stats_query = 'EXEC [dbo].[sp_TeamSeasonStats]'

SHOT_PLOT_COLUMNS = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX', 'LocationY', 'Period', 'TeamID',
                     'PlayerID']

TEAM_COLUMNS = ['TeamID', 'TeamCode', 'TeamLogo']

TEAM_STATS_COLUMNS = ['tid', 'teamcode', 'season', 'ast', 'games', 'blk', 'blka', 'dreb', 'fbpts', 'fbptsa',
                      'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
                      'pts', 'reb', 'stl', 'tov', 'tpa', 'tpm']

CURRENT_ROSTER_COLUMNS = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                          'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division',
                          'Conference']
