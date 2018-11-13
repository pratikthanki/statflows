latestGame = '''
SELECT 
SUBSTRING(gb.Game,CHARINDEX('(',gb.Game)+1,CHARINDEX(')',gb.Game)-CHARINDEX('(',gb.Game)-1) as LatestDate
,p.[TeamID]
,CASE WHEN l.Ta = gb.[AwayTeamCode] THEN gb.[HomeTeamCode] ELSE gb.[AwayTeamCode] END as Opposition
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

JOIN GameBoxScore gb ON gb.GameID = p.GameID

INNER JOIN (
SELECT 
MAX(Games.[Date]) as LatestDate
,[TeamID]
,[Ta]
,[PlayerID]
FROM [dbo].[PlayerGameSummary]
JOIN Games ON Games.GameID = PlayerGameSummary.GameID
GROUP BY [TeamID], [PlayerID], [Ta]
HAVING MAX(Games.[Date]) > '2018-09-01' AND LEN([TeamID]) = 10 ) l 

ON l.TeamID = p.TeamID and l.PlayerID = p.PlayerID

'''

teamRosters = 'SELECT * FROM TeamRosters2018'
