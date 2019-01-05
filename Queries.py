latestGame = 'EXEC [sp_LatestPlayerApps]'
teamRosters = "EXEC [dbo].[sp_TeamRosters] '2018'"
teams = 'SELECT [TeamID] ,[TeamCode] ,[TeamLogo] FROM [dbo].[Teams] WHERE LEN(TeamID) = 10'
