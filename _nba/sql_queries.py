
SHOT_PLOT_COLUMNS = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX', 'LocationY', 'Period', 'TeamID',
                     'Opposition TeamID', 'PlayerID', 'GameID', 'Date', 'Season', 'Venue']

shot_chart_query = '''
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
AND g.season = '2019-2020'
AND gp.etype IN (1,2) 
'''

team_shot_chart_query = '''
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
WHERE gp.tid = {0} 
AND g.season = '2019-2020'
AND gp.etype IN (1,2) 
'''

CURRENT_ROSTER_COLUMNS = ['team_id', 'Season', 'league_id', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                          'DoB', 'Age', 'Experience', 'School', 'player_id']

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

team_trend_query = '''
SELECT 
    t.team_id
    ,t.team_code
    ,g.season
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
    WHERE LEN(tid) = 10
    AND tid = {0}
    GROUP BY [gid], [tid]
) gs
JOIN teams t ON t.team_id = gs.tid
JOIN games g ON g.game_id = gs.gid
GROUP BY 
t.team_id
,t.team_code
,g.season
'''

team_compare_query = '''
SELECT 
    team_id
    ,team_code
    ,season
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
        t.team_id
        ,t.team_code
        ,g.season
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
    JOIN teams t ON t.team_id = gs.tid
    JOIN games g ON g.game_id = gs.gid
    WHERE LEN(tid) = 10
    AND g.season = '{0}'
    GROUP BY 
        t.team_id
        ,t.team_code
        ,g.season
        ,g.[game_id]
) gs
GROUP BY 
    team_id
    ,team_code
    ,season
'''

TEAM_STATS_COLUMNS = ['tid', 'teamcode', 'season', 'ast', 'games', 'blk', 'blka', 'dreb', 'fbpts', 'fbptsa',
                      'fbptsm', 'fga', 'fgm', 'fta', 'ftm', 'oreb', 'pf', 'pip', 'pipa', 'pipm',
                      'pts', 'reb', 'stl', 'tov', 'tpa', 'tpm']
