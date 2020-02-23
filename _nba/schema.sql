
CREATE TABLE [dbo].[games]
(
	[game_id] [varchar](50) NULL,
	[game_code] [varchar](50) NULL,
	[venue] [varchar](50) NULL,
	[date] [datetime] NULL,
	[away_team_id] [bigint] NULL,
	[away_score] [int] NULL,
	[home_team_id] [bigint] NULL,
	[home_score] [int] NULL,
	[season] [varchar](10) NULL,
    [LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
);
GO


CREATE TABLE [dbo].[game_pbp]
(
    [game_pbp_id] [int] IDENTITY(1, 1),
    [cl] [nvarchar](10) NULL,
    [de] [nvarchar](255) NULL,
    [epid] [bigint] NULL,
    [etype] [bigint] NULL,
    [evt] [bigint] NULL,
    [gid] [bigint] NOT NULL,
    [hs] [bigint] NULL,
    [locX] [bigint] NULL,
    [locY] [bigint] NULL,
    [mid] [bigint] NULL,
    [mtype] [bigint] NULL,
    [oftid] [bigint] NULL,
    [opid] [bigint] NULL,
    [opt1] [bigint] NULL,
    [opt2] [bigint] NULL,
    [ord] [float] NULL,
    [period] [bigint] NULL,
    [pid] [bigint] NOT NULL,
    [tid] [bigint] NOT NULL,
    [vs] [bigint] NULL,
    [LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
);
GO


CREATE TABLE [dbo].[game_stats]
(
    [game_stats_id] [int] IDENTITY(1, 1),
	[ast] [bigint] NULL,
	[blk] [bigint] NULL,
	[blka] [bigint] NULL,
	[court] [bigint] NULL,
	[dreb] [bigint] NULL,
	[fbpts] [bigint] NULL,
	[fbptsa] [bigint] NULL,
	[fbptsm] [bigint] NULL,
	[fga] [bigint] NULL,
	[fgm] [bigint] NULL,
	[fn] [nvarchar](30) NULL,
	[fta] [bigint] NULL,
	[ftm] [bigint] NULL,
	[gid] [bigint] NOT NULL,
	[ln] [nvarchar](30) NULL,
	[memo] [nvarchar](50) NULL,
	[mid] [bigint] NULL,
	[min] [bigint] NULL,
	[num] [nvarchar](3) NULL,
	[oreb] [bigint] NULL,
	[pf] [bigint] NULL,
	[pid] [bigint] NOT NULL,
	[pip] [bigint] NULL,
	[pipa] [bigint] NULL,
	[pipm] [bigint] NULL,
	[pm] [bigint] NULL,
	[pos] [nvarchar](10) NULL,
	[pts] [bigint] NULL,
	[reb] [bigint] NULL,
	[sec] [bigint] NULL,
	[status] [nvarchar](2) NULL,
	[stl] [bigint] NULL,
	[ta] [nvarchar](5) NULL,
	[tf] [bigint] NULL,
	[tid] [bigint] NOT NULL,
	[totsec] [bigint] NULL,
	[tov] [bigint] NULL,
	[tpa] [bigint] NULL,
	[tpm] [bigint] NULL,
    [LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
);
GO


CREATE TABLE [dbo].[teams]
(
	[team_id] [bigint] NOT NULL,
	[team_code] [varchar](255) NULL,
	[team_logo]  AS (case when len([TeamID])=(10) then ('https://stats.nba.com/media/img/teams/logos/'+[TeamCode])+'_logo.svg' else '' end),
	[LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
);
GO


CREATE TABLE [dbo].[rosters]
(
	[teamid] [varchar](255) NULL,
	[season] [varchar](255) NULL,
	[leagueid] [varchar](255) NULL,
	[player] [varchar](255) NULL,
	[num] [varchar](255) NULL,
	[position] [varchar](255) NULL,
	[height] [varchar](255) NULL,
	[weight] [varchar](255) NULL,
	[birth_date] [varchar](255) NULL,
	[age] [varchar](255) NULL,
	[exp] [varchar](255) NULL,
	[school] [varchar](255) NULL,
	[player_id] [varchar](255) NULL,
	[LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
);
GO
