latestGame = '''
SELECT 
    CAST(s.[Date] as [date]) as LatestDate
    ,FORMAT(CAST(s.[Date] as [date]), 'dd-MMM') as GameDate
    ,p.TeamID
    ,CASE WHEN p.[TeamID] = s.HomeTeamID THEN s.AwayTeamID ELSE s.HomeTeamID END as OppositionId
    ,t.TeamCode as OppositionTeamCode
    ,t.TeamLogo as OppositionTeamLogo
    ,p.PlayerID
    ,p.[Fn] + ' ' + p.[Ln] as FullName
    ,p.[Fn] + ' ' + p.[Ln] + ' (' + p.[Pos] + ')' as FullNamePos
    ,p.[Num]
    ,p.[Pos]
    ,p.[Min]
    ,p.[Pts]
    ,p.[Ast]
    ,p.[Blk]
    ,p.[Reb]
    ,p.[Fga]
    ,p.[Fgm]
    ,p.[Fta]
    ,p.[Ftm]
    ,p.[Stl]
    ,p.[Tov]
    ,p.[Pf]
    ,p.[Pip]
    ,p.[Pipa]
    ,p.[Pipm]
FROM [dbo].[PlayerGameSummary] p
    JOIN Schedule s ON s.GameID = p.GameID
    JOIN Teams t ON t.TeamID = CASE WHEN p.[TeamID] = s.HomeTeamID THEN s.AwayTeamID ELSE s.HomeTeamID END
WHERE s.[Date] > '2018-09-01' --AND p.[Min] > 0
ORDER BY CAST(s.[Date] as [date]) DESC

'''

teamRosters = 'SELECT * FROM TeamRosters2018'
