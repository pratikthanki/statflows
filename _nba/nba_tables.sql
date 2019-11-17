CREATE TABLE [dbo].[DrillResults](
	[TempPlayerId] [float] NULL,
	[PlayerId] [float] NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[PlayerName] [varchar](max) NULL,
	[Position] [varchar](max) NULL,
	[StandingVerticalLeap] [float] NULL,
	[MaxVerticalLeap] [float] NULL,
	[LaneAgilityTime] [float] NULL,
	[ModifiedLaneAgilityTime] [float] NULL,
	[ThreeQuarterSprint] [float] NULL,
	[BenchPress] [float] NULL,
	[Seasonyear] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[DrillResults] ADD  CONSTRAINT [last_updated_DrillResults]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[GameBoxScore](
	[Game] [varchar](max) NULL,
	[GameID] [bigint] NOT NULL,
	[BoxScoreBreakdown] [varchar](max) NULL,
	[HomeTeamCode] [varchar](max) NULL,
	[HomeTeamName] [varchar](max) NULL,
	[HomeTeamNickname] [varchar](max) NULL,
	[AwayTeamCode] [varchar](max) NULL,
	[AwayTeamName] [varchar](max) NULL,
	[AwayTeamNickname] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[GameBoxScore] ADD  CONSTRAINT [last_updated_GameBoxScore]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[GamePlays](
	[cl] [varchar](max) NULL,
	[de] [varchar](max) NULL,
	[epid] [varchar](max) NULL,
	[etype] [bigint] NULL,
	[evt] [bigint] NULL,
	[gid] [bigint] NOT NULL,
	[hs] [bigint] NULL,
	[locX] [bigint] NULL,
	[locY] [bigint] NULL,
	[mid] [bigint] NULL,
	[mtype] [bigint] NULL,
	[oftid] [bigint] NULL,
	[opid] [varchar](max) NULL,
	[opt1] [bigint] NULL,
	[opt2] [bigint] NULL,
	[ord] [float] NULL,
	[period] [bigint] NULL,
	[pid] [bigint] NOT NULL,
	[tid] [bigint] NOT NULL,
	[vs] [bigint] NULL,
	[Id] [uniqueidentifier] NOT NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
CREATE CLUSTERED INDEX [IX_GamePlays_GameID] ON [dbo].[GamePlays]
(
	[gid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_GamePlays_1] ON [dbo].[GamePlays]
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_GamePlays_2] ON [dbo].[GamePlays]
(
	[gid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
ALTER TABLE [dbo].[GamePlays] ADD  DEFAULT (newid()) FOR [Id]
GO
ALTER TABLE [dbo].[GamePlays] ADD  CONSTRAINT [last_updated_pbp]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[LatestInjuries](
	[Team] [varchar](3) NULL,
	[Name] [varchar](255) NULL,
	[Date] [datetime2](7) NULL,
	[Status] [varchar](255) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[LatestInjuries] ADD  CONSTRAINT [last_updated_LatestInjuries]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[LeagueStandings](
	[Abbr] [varchar](255) NULL,
	[Conference] [varchar](255) NULL,
	[TeamId] [varchar](255) NULL,
	[TeamName] [varchar](255) NULL,
	[ConfRank] [varchar](255) NULL,
	[Wins] [varchar](255) NULL,
	[Losses] [varchar](255) NULL,
	[Streak] [varchar](255) NULL,
	[Win%] [varchar](255) NULL,
	[DivLosses] [varchar](255) NULL,
	[DivWins] [varchar](255) NULL,
	[DivRank] [varchar](255) NULL,
	[Last10] [varchar](255) NULL,
	[HomeWins] [varchar](255) NULL,
	[HomeLosses] [varchar](255) NULL,
	[RoadWins] [varchar](255) NULL,
	[RoadLosses] [varchar](255) NULL,
	[RoadStreak] [varchar](255) NULL,
	[HomeStreak] [varchar](255) NULL,
	[LastUpdates] [datetime] NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[LeagueStandings] ADD  CONSTRAINT [last_updated_LeagueStandings]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[NonStationaryShooting](
	[TempPlayerId] [float] NULL,
	[PlayerId] [float] NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[PlayerName] [varchar](max) NULL,
	[Position] [varchar](max) NULL,
	[OffDribFifteenBreakLeftMade] [float] NULL,
	[OffDribFifteenBreakLeftAttempt] [float] NULL,
	[OffDribFifteenBreakLeftPct] [float] NULL,
	[OffDribFifteenTopKeyMade] [float] NULL,
	[OffDribFifteenTopKeyAttempt] [float] NULL,
	[OffDribFifteenTopKeyPct] [float] NULL,
	[OffDribFifteenBreakRightMade] [float] NULL,
	[OffDribFifteenBreakRightAttempt] [float] NULL,
	[OffDribFifteenBreakRightPct] [float] NULL,
	[OffDribCollegeBreakLeftMade] [float] NULL,
	[OffDribCollegeBreakLeftAttempt] [float] NULL,
	[OffDribCollegeBreakLeftPct] [float] NULL,
	[OffDribCollegeTopKeyMade] [float] NULL,
	[OffDribCollegeTopKeyAttempt] [float] NULL,
	[OffDribCollegeTopKeyPct] [float] NULL,
	[OffDribCollegeBreakRightMade] [float] NULL,
	[OffDribCollegeBreakRightAttempt] [float] NULL,
	[OffDribCollegeBreakRightPct] [float] NULL,
	[OnMoveFifteenMade] [float] NULL,
	[OnMoveFifteenAttempt] [float] NULL,
	[OnMoveFifteenPct] [float] NULL,
	[OnMoveCollegeMade] [float] NULL,
	[OnMoveCollegeAttempt] [float] NULL,
	[OnMoveCollegePct] [float] NULL,
	[Seasonyear] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[NonStationaryShooting] ADD  CONSTRAINT [last_updated_NonStationaryShooting]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[PlayerAnthro](
	[TempPlayerId] [float] NULL,
	[PlayerId] [float] NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[PlayerName] [varchar](max) NULL,
	[Position] [varchar](max) NULL,
	[HeightWoShoes] [float] NULL,
	[HeightWoShoesFtIn] [varchar](max) NULL,
	[HeightWShoes] [float] NULL,
	[HeightWShoesFtIn] [varchar](max) NULL,
	[Weight] [varchar](max) NULL,
	[Wingspan] [float] NULL,
	[WingspanFtIn] [varchar](max) NULL,
	[StandingReach] [float] NULL,
	[StandingReachFtIn] [varchar](max) NULL,
	[BodyFatPct] [float] NULL,
	[HandLength] [float] NULL,
	[HandWidth] [float] NULL,
	[Seasonyear] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[PlayerAnthro] ADD  CONSTRAINT [last_updated_PlayerAnthro]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[PlayerGameSummary](
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
	[fn] [varchar](max) NULL,
	[fta] [bigint] NULL,
	[ftm] [bigint] NULL,
	[gid] [bigint] NOT NULL,
	[ln] [varchar](max) NULL,
	[memo] [varchar](max) NULL,
	[mid] [bigint] NULL,
	[min] [bigint] NULL,
	[num] [varchar](max) NULL,
	[oreb] [bigint] NULL,
	[pf] [bigint] NULL,
	[pid] [bigint] NOT NULL,
	[pip] [bigint] NULL,
	[pipa] [bigint] NULL,
	[pipm] [bigint] NULL,
	[pm] [bigint] NULL,
	[pos] [varchar](max) NULL,
	[pts] [bigint] NULL,
	[reb] [bigint] NULL,
	[sec] [bigint] NULL,
	[status] [varchar](max) NULL,
	[stl] [bigint] NULL,
	[ta] [varchar](max) NULL,
	[tf] [bigint] NULL,
	[tid] [bigint] NOT NULL,
	[totsec] [bigint] NULL,
	[tov] [bigint] NULL,
	[tpa] [bigint] NULL,
	[tpm] [bigint] NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_PlayerGameSummary_1] ON [dbo].[PlayerGameSummary]
(
	[gid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_PlayerGameSummary_2] ON [dbo].[PlayerGameSummary]
(
	[tid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
CREATE NONCLUSTERED INDEX [IX_PlayerGameSummary_3] ON [dbo].[PlayerGameSummary]
(
	[pid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
GO
ALTER TABLE [dbo].[PlayerGameSummary] ADD  CONSTRAINT [last_updated_game_summary]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[Players](
	[PlayerID] [bigint] NOT NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[Players] ADD  CONSTRAINT [last_updated]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[Schedule](
	[GameID] [varchar](50) NULL,
	[GameCode] [varchar](50) NULL,
	[Venue] [varchar](50) NULL,
	[Date] [datetime] NULL,
	[DateString] [varchar](10) NULL,
	[AwayTeamID] [bigint] NULL,
	[AwayScore] [int] NULL,
	[HomeTeamID] [bigint] NULL,
	[HomeScore] [int] NULL,
	[LastUpdated] [datetime] NOT NULL,
	[Season] [varchar](9) NULL
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Schedule] ADD  CONSTRAINT [last_updated_Schedule]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[SpotShooting](
	[TempPlayerId] [float] NULL,
	[PlayerId] [float] NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[PlayerName] [varchar](max) NULL,
	[Position] [varchar](max) NULL,
	[FifteenCornerLeftMade] [float] NULL,
	[FifteenCornerLeftAttempt] [float] NULL,
	[FifteenCornerLeftPct] [float] NULL,
	[FifteenBreakLeftMade] [float] NULL,
	[FifteenBreakLeftAttempt] [float] NULL,
	[FifteenBreakLeftPct] [float] NULL,
	[FifteenTopKeyMade] [float] NULL,
	[FifteenTopKeyAttempt] [float] NULL,
	[FifteenTopKeyPct] [float] NULL,
	[FifteenBreakRightMade] [float] NULL,
	[FifteenBreakRightAttempt] [float] NULL,
	[FifteenBreakRightPct] [float] NULL,
	[FifteenCornerRightMade] [float] NULL,
	[FifteenCornerRightAttempt] [float] NULL,
	[FifteenCornerRightPct] [float] NULL,
	[CollegeCornerLeftMade] [float] NULL,
	[CollegeCornerLeftAttempt] [float] NULL,
	[CollegeCornerLeftPct] [float] NULL,
	[CollegeBreakLeftMade] [float] NULL,
	[CollegeBreakLeftAttempt] [float] NULL,
	[CollegeBreakLeftPct] [float] NULL,
	[CollegeTopKeyMade] [float] NULL,
	[CollegeTopKeyAttempt] [float] NULL,
	[CollegeTopKeyPct] [float] NULL,
	[CollegeBreakRightMade] [float] NULL,
	[CollegeBreakRightAttempt] [float] NULL,
	[CollegeBreakRightPct] [float] NULL,
	[CollegeCornerRightMade] [float] NULL,
	[CollegeCornerRightAttempt] [float] NULL,
	[CollegeCornerRightPct] [float] NULL,
	[NbaCornerLeftMade] [float] NULL,
	[NbaCornerLeftAttempt] [float] NULL,
	[NbaCornerLeftPct] [float] NULL,
	[NbaBreakLeftMade] [float] NULL,
	[NbaBreakLeftAttempt] [float] NULL,
	[NbaBreakLeftPct] [float] NULL,
	[NbaTopKeyMade] [float] NULL,
	[NbaTopKeyAttempt] [float] NULL,
	[NbaTopKeyPct] [float] NULL,
	[NbaBreakRightMade] [float] NULL,
	[NbaBreakRightAttempt] [float] NULL,
	[NbaBreakRightPct] [float] NULL,
	[NbaCornerRightMade] [float] NULL,
	[NbaCornerRightAttempt] [float] NULL,
	[NbaCornerRightPct] [float] NULL,
	[Seasonyear] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[SpotShooting] ADD  CONSTRAINT [last_updated_SpotShooting]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[Stats](
	[Season] [varchar](max) NULL,
	[PlayerId] [float] NULL,
	[FirstName] [varchar](max) NULL,
	[LastName] [varchar](max) NULL,
	[PlayerName] [varchar](max) NULL,
	[Position] [varchar](max) NULL,
	[HeightWoShoes] [float] NULL,
	[HeightWoShoesFtIn] [varchar](max) NULL,
	[HeightWShoes] [float] NULL,
	[HeightWShoesFtIn] [varchar](max) NULL,
	[Weight] [varchar](max) NULL,
	[Wingspan] [float] NULL,
	[WingspanFtIn] [varchar](max) NULL,
	[StandingReach] [float] NULL,
	[StandingReachFtIn] [varchar](max) NULL,
	[BodyFatPct] [float] NULL,
	[HandLength] [float] NULL,
	[HandWidth] [float] NULL,
	[StandingVerticalLeap] [float] NULL,
	[MaxVerticalLeap] [float] NULL,
	[LaneAgilityTime] [float] NULL,
	[ModifiedLaneAgilityTime] [float] NULL,
	[ThreeQuarterSprint] [float] NULL,
	[BenchPress] [float] NULL,
	[SpotFifteenCornerLeft] [varchar](max) NULL,
	[SpotFifteenBreakLeft] [varchar](max) NULL,
	[SpotFifteenTopKey] [varchar](max) NULL,
	[SpotFifteenBreakRight] [varchar](max) NULL,
	[SpotFifteenCornerRight] [varchar](max) NULL,
	[SpotCollegeCornerLeft] [varchar](max) NULL,
	[SpotCollegeBreakLeft] [varchar](max) NULL,
	[SpotCollegeTopKey] [varchar](max) NULL,
	[SpotCollegeBreakRight] [varchar](max) NULL,
	[SpotCollegeCornerRight] [varchar](max) NULL,
	[SpotNbaCornerLeft] [varchar](max) NULL,
	[SpotNbaBreakLeft] [varchar](max) NULL,
	[SpotNbaTopKey] [varchar](max) NULL,
	[SpotNbaBreakRight] [varchar](max) NULL,
	[SpotNbaCornerRight] [varchar](max) NULL,
	[OffDribFifteenBreakLeft] [varchar](max) NULL,
	[OffDribFifteenTopKey] [varchar](max) NULL,
	[OffDribFifteenBreakRight] [varchar](max) NULL,
	[OffDribCollegeBreakLeft] [varchar](max) NULL,
	[OffDribCollegeTopKey] [varchar](max) NULL,
	[OffDribCollegeBreakRight] [varchar](max) NULL,
	[OnMoveFifteen] [varchar](max) NULL,
	[OnMoveCollege] [varchar](max) NULL,
	[SeasonYear] [varchar](max) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[Stats] ADD  CONSTRAINT [last_updated_Stats]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[TeamRosters](
	[TeamID] [varchar](255) NULL,
	[SEASON] [varchar](255) NULL,
	[LeagueID] [varchar](255) NULL,
	[PLAYER] [varchar](255) NULL,
	[NUM] [varchar](255) NULL,
	[POSITION] [varchar](255) NULL,
	[HEIGHT] [varchar](255) NULL,
	[WEIGHT] [varchar](255) NULL,
	[BIRTH_DATE] [varchar](255) NULL,
	[AGE] [varchar](255) NULL,
	[EXP] [varchar](255) NULL,
	[SCHOOL] [varchar](255) NULL,
	[PLAYER_ID] [varchar](255) NULL,
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[TeamRosters] ADD  CONSTRAINT [last_updated_TeamRosters]  DEFAULT (getdate()) FOR [LastUpdated]
GO


CREATE TABLE [dbo].[Teams](
	[TeamID] [bigint] NOT NULL,
	[TeamCode] [varchar](max) NULL,
	[TeamLogo]  AS (case when len([TeamID])=(10) then ('https://stats.nba.com/media/img/teams/logos/'+[TeamCode])+'_logo.svg' else '' end),
	[LastUpdated] [datetime] NOT NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[Teams] ADD  CONSTRAINT [last_updated_team]  DEFAULT (getdate()) FOR [LastUpdated]
GO
