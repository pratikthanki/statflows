latestGame = '''
SELECT 
CAST(g.[Date] as [date]) as LatestDate
,g.[Venue]
,p.[TeamID]
,p.[PlayerID]
,p.[Fn] + ' ' + p.[Ln] as FullName
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

JOIN Games g ON g.GameID = p.GameID

INNER JOIN (
SELECT 
MAX(Games.[Date]) as LatestDate
,[TeamID]
,[PlayerID]
FROM [dbo].[PlayerGameSummary]
JOIN Games ON Games.GameID = PlayerGameSummary.GameID
GROUP BY [TeamID], [PlayerID]
HAVING MAX(Games.[Date]) > '2018-09-01' AND LEN([TeamID]) = 10 ) l 

ON l.LatestDate = g.[Date] and l.PlayerID = p.PlayerID

ORDER BY p.TeamID, g.[Date]

-- ['LatestDate', 'Venue', 'TeamID', 'PlayerID', 'FullName', 'JerseyNum', 'Pos', 'Min', 'Pts', 'Ast', Blk, Reb, Fga, Fgm, Fta, Ftm, Stl, Tov, Pf, Pip, Pipa, Pipm]
'''

teamRosters = 'SELECT * FROM TeamRosters2018'
