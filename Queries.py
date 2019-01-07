latestGame = 'EXEC [sp_LatestPlayerApps]'
teamRosters = "EXEC [dbo].[sp_TeamRosters] '2018'"
teams = "SELECT [TeamID] ,[TeamCode] ,COALESCE([TeamLogo], 'http://www.performgroup.com/wp-content/uploads/2015/09/nba-logo-png.png') as TeamLogo FROM [dbo].[Teams]"

shotChart = 'EXEC [dbo].[sp_PlayerShotChart]'

standings = '''
SELECT 
[Conference]
,[TeamId]
,CAST([Wins] as VARCHAR(10)) + '-' + CAST([Losses] as VARCHAR(10)) 
,[ConfRank]
,[Streak]
,[Win%]
,[Last10]
,CAST([DivWins] as VARCHAR(10)) + '-' + CAST([DivLosses] as VARCHAR(10)) 
,[DivRank]
,[HomeWins]
,[HomeLosses]
,[HomeStreak]
,[RoadWins]
,[RoadLosses]
,[RoadStreak]
FROM [dbo].[LeagueStandings]
'''
