
SHOT_PLOT_COLUMNS = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX', 'LocationY', 'Period', 'TeamID',
                     'Opposition TeamID', 'PlayerID', 'GameID', 'Date', 'Season', 'Venue']

shot_chart_query = '''
SET NOCOUNT ON;
BEGIN
SELECT TOP (1000)
[cl]
,[de]
,[etype]
,[evt]
,[locX]
,[locY]
,[period]
,[tid]
,CASE WHEN tid = g.home_team_id THEN g.away_team_id ELSE home_team_id END [opp_tid]
,[pid]
,g.[game_id]
,g.[date]
,g.[season]
,g.[venue]
FROM [NBA].[dbo].[game_pbp] gp
JOIN games g ON g.game_id = gp.gid
WHERE gp.pid = {0} 
AND gp.tid = {1} 
AND g.season = '2019-2020'
AND gp.etype IN (1,2) 
AND [tid] IN (SELECT [team_id] FROM [nba].[dbo].[teams])
END
'''

CURRENT_ROSTER_COLUMNS = ['team_id', 'Season', 'league_id', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                          'DoB', 'Age', 'Experience', 'School', 'player_id']

team_roster_query = '''
SET NOCOUNT ON;
BEGIN
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
        [player_id]
        ,MAX([LastUpdated]) as Latest
    FROM [NBA].[dbo].[rosters]
    WHERE [season] = 2019
    AND [teamid] = {0}
    GROUP BY [player_id]
) l 
    ON l.player_id = r.player_id
    AND l.Latest = r.LastUpdated
END
'''

team_trend_query = '''
SET NOCOUNT ON;
BEGIN
SELECT 
    [tid]
    ,g.[season]
    ,AVG([ast])
    ,COUNT(gid) AS [games]
    ,AVG([blk])
    ,AVG([blka])
    ,AVG([dreb])
    ,AVG([fbpts])
    ,AVG([fbptsa])
    ,AVG([fbptsm])
    ,AVG([fga])
    ,AVG([fgm])
    ,AVG([fta])
    ,AVG([ftm])
    ,AVG([oreb])
    ,AVG([pf])
    ,AVG([pip])
    ,AVG([pipa])
    ,AVG([pipm])
    ,AVG([pts])
    ,AVG([reb])
    ,AVG([stl])
    ,AVG([tov])
    ,AVG([tpa])
    ,AVG([tpm])
FROM (
    SELECT 
        [gid]
        ,[tid]
        ,SUM([ast]) ast
        ,COUNT(*) games
        ,SUM([blk]) blk
        ,SUM([blka]) blka
        ,SUM([dreb]) dreb
        ,SUM([fbpts]) fbpts
        ,SUM([fbptsa]) fbptsa
        ,SUM([fbptsm]) fbptsm
        ,SUM([fga]) fga
        ,SUM([fgm]) fgm
        ,SUM([fta]) fta
        ,SUM([ftm]) ftm
        ,SUM([oreb]) oreb
        ,SUM([pf]) pf
        ,SUM([pip]) pip
        ,SUM([pipa]) pipa
        ,SUM([pipm]) pipm
        ,SUM([pts]) pts
        ,SUM([reb]) reb
        ,SUM([stl]) stl
        ,SUM([tov]) tov
        ,SUM([tpa]) tpa
        ,SUM([tpm]) tpm
    FROM [NBA].[dbo].[game_stats]
    WHERE [tid] = {0}
    GROUP BY [gid], [tid]
) gs
JOIN games g ON g.game_id = gs.gid
GROUP BY 
[tid]
,g.season
END
'''

team_compare_query = '''
SET NOCOUNT ON;
BEGIN
SELECT 
    [tid]
    ,[season]
    ,AVG([ast])
    ,COUNT(game_id) AS [games]
    ,AVG([blk])
    ,AVG([blka])
    ,AVG([dreb])
    ,AVG([fbpts])
    ,AVG([fbptsa])
    ,AVG([fbptsm])
    ,AVG([fga])
    ,AVG([fgm])
    ,AVG([fta])
    ,AVG([ftm])
    ,AVG([oreb])
    ,AVG([pf])
    ,AVG([pip])
    ,AVG([pipa])
    ,AVG([pipm])
    ,AVG([pts])
    ,AVG([reb])
    ,AVG([stl])
    ,AVG([tov])
    ,AVG([tpa])
    ,AVG([tpm])
FROM (
    SELECT 
        [tid]
        ,g.[season]
        ,g.[game_id]
        ,SUM([ast]) ast
        ,COUNT(*) games
        ,SUM([blk]) blk
        ,SUM([blka]) blka
        ,SUM([dreb]) dreb
        ,SUM([fbpts]) fbpts
        ,SUM([fbptsa]) fbptsa
        ,SUM([fbptsm]) fbptsm
        ,SUM([fga]) fga
        ,SUM([fgm]) fgm
        ,SUM([fta]) fta
        ,SUM([ftm]) ftm
        ,SUM([oreb]) oreb
        ,SUM([pf]) pf
        ,SUM([pip]) pip
        ,SUM([pipa]) pipa
        ,SUM([pipm]) pipm
        ,SUM([pts]) pts
        ,SUM([reb]) reb
        ,SUM([stl]) stl
        ,SUM([tov]) tov
        ,SUM([tpa]) tpa
        ,SUM([tpm]) tpm
    FROM [NBA].[dbo].[game_stats] gs
    JOIN games g ON g.game_id = gs.gid
    WHERE [tid] IN (SELECT [team_id] FROM [nba].[dbo].[teams])
    AND g.season = '{0}'
    GROUP BY 
        [tid]
        ,g.[season]
        ,g.[game_id]
) gs
GROUP BY 
    [tid]
    ,[season]
END
'''

TEAM_STATS_COLUMNS = ['tid', 'season', 'ast', 'games', 'blk', 'blka', 'dreb', 'fbpts', 'fbptsa',
                      'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
                      'pts', 'reb', 'stl', 'tov', 'tpa', 'tpm']

POSITION_CLUSTERS_COLUMNS = ['season', 'player_id',
                             'player_name', 'labels', 'tags', 'x1', 'x2']

position_clusters_query = '''
SET NOCOUNT ON;
BEGIN
SELECT 
[Season]
,[Player_ID]
,[Player]
,[labels]
,[tags]
,[X1]
,[X2]
FROM [nba].[dbo].[position_clusters]
WHERE [Season] = '{0}'
END
'''


SHOOTING_STATS_COLUMNS = ['season', 'player_id', 'Player', 'G', 'GS', 'FBPTS', 'FBPTSM', 'FBPTSA', 'FBPTS%', 'FGM', 'FGA',
                          'FG%', 'FTM', 'FTA', 'FT%', 'PIP', 'PIPM', 'PIPA', 'PIP%', 'PTS', '3PM', '3PA', '3P%']

player_shooting_stats_query = '''
SET NOCOUNT ON;
BEGIN
SELECT 
    g.[season]
    ,gs.[pid]
    ,r.[player]
    ,COUNT(gs.[gid]) [appearances]
    ,SUM(CASE WHEN [pos] = '' THEN 0 ELSE 1 END) AS [starts]
    ,SUM(CAST([fbpts] AS float)) fbpts
    ,SUM(CAST([fbptsm] AS float)) fbptsm
    ,SUM(CAST([fbptsa] AS float)) fbptsa
    ,CASE WHEN SUM(CAST([fbptsa] AS float)) > 0 THEN ROUND(SUM(CAST([fbptsm] AS float)) / SUM(CAST([fbptsa] AS float)), 2) ELSE 0 END [fbpts%]
    ,SUM(CAST([fgm] AS float)) fgm
    ,SUM(CAST([fga] AS float)) fga
    ,CASE WHEN SUM(CAST([fga] AS float)) > 0 THEN ROUND(SUM(CAST([fgm] AS float)) / SUM(CAST([fga] AS float)), 2) ELSE 0 END [fg%]
    ,SUM(CAST([ftm] AS float)) ftm
    ,SUM(CAST([fta] AS float)) fta
    ,CASE WHEN SUM(CAST([fta] AS float)) > 0 THEN ROUND(SUM(CAST([ftm] AS float)) / SUM(CAST([fta] AS float)), 2) ELSE 0 END [ft%]
    ,SUM(CAST([pip] AS float)) pip
    ,SUM(CAST([pipm] AS float)) pipm
    ,SUM(CAST([pipa] AS float)) pipa
    ,CASE WHEN SUM(CAST([pipa] AS float)) > 0 THEN ROUND(SUM(CAST([pipm] AS float)) / SUM(CAST([pipa] AS float)), 2) ELSE 0 END [pip%]
    ,SUM(CAST([pts] AS float)) pts
    ,SUM(CAST([tpm] AS float)) tpm
    ,SUM(CAST([tpa] AS float)) tpa
    ,CASE WHEN SUM(CAST([tpa] AS float)) > 0 THEN ROUND(SUM(CAST([tpm] AS float)) / SUM(CAST([tpa] AS float)), 2) ELSE 0 END [3p%]
FROM [nba].[dbo].[game_stats] gs
JOIN [nba].[dbo].[rosters] r ON r.player_id = gs.pid
JOIN [nba].[dbo].[games] g ON g.game_id = gs.gid
JOIN (
    SELECT 
    [season]
    ,[pid]
    ,COUNT([gid]) AS [appearances]
    FROM [nba].[dbo].[game_stats] gs
    JOIN games g ON g.game_id = gs.gid
    WHERE [tid] = {0}
    AND [season] = '2019-2020'
    GROUP BY [season], [pid]
) a
    ON a.[season] = g.[season] AND a.pid = gs.pid
GROUP BY g.[season] ,gs.[pid] ,r.[player]
END
'''
