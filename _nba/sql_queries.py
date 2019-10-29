latest_game_query = 'EXEC [dbo].[sp_LatestPlayerApps]'
shot_chart_query = "EXEC [dbo].[sp_ShotChart] @PlayerId='{0}', @Period='{1}', @Venue='{2}'"
team_roster_query = 'EXEC [dbo].[sp_TeamRosters]'
team_season_stats_query = 'EXEC [dbo].[sp_TeamSeasonStats]'

team_query = 'SELECT * FROM [dbo].[vwTeams]'
standings_query = 'SELECT * FROM [dbo].[vwStandings]'

SHOT_PLOT_COLUMNS = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX', 'LocationY', 'Period', 'TeamID',
                     'PlayerID', 'Date', 'Season', 'Venue']

TEAM_COLUMNS = ['TeamID', 'TeamCode', 'TeamLogo', 'Division', 'Conference']

TEAM_STATS_COLUMNS = ['tid', 'teamcode', 'season', 'ast', 'games', 'blk', 'blka', 'dreb', 'fbpts', 'fbptsa',
                      'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
                      'pts', 'reb', 'stl', 'tov', 'tpa', 'tpm']

CURRENT_ROSTER_COLUMNS = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                          'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division',
                          'Conference']
