CREATE TABLE IF NOT EXISTS LeagueStandings(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	Abbr varchar(255),
	Conference varchar(255),
	TeamId varchar(255),
	TeamName varchar(255),
	ConfRank varchar(255),
	Wins varchar(255),
	Losses varchar(255),
	Streak varchar(255),
	`Win%` varchar(255),
	DivLosses varchar(255),
	DivWins varchar(255),
	DivRank varchar(255),
	Last10 varchar(255),
	HomeWins varchar(255),
	HomeLosses varchar(255),
	RoadWins varchar(255),
	RoadLosses varchar(255),
	RoadStreak varchar(255),
	HomeStreak varchar(255),
	LastUpdates datetime,
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Schedule(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	GameID varchar(50),
	GameCode varchar(50),
	Venue varchar(50),
	Date datetime,
	DateString varchar(10),
	AwayTeamID bigint,
	AwayScore int,
	HomeTeamID bigint,
	HomeScore int,
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	Season varchar(9)
);


CREATE TABLE IF NOT EXISTS LatestInjuries(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	Team varchar(3),
	Name varchar(255),
	Date datetime(6),
	Status varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS GameBoxScore(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	Game varchar(255),
	GameID bigint NOT NULL,
	BoxScoreBreakdown varchar(255),
	HomeTeamCode varchar(255),
	HomeTeamName varchar(255),
	HomeTeamNickname varchar(255),
	AwayTeamCode varchar(255),
	AwayTeamName varchar(255),
	AwayTeamNickname varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS GamePlays(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	cl varchar(255),
	de varchar(255),
	epid varchar(255),
	etype bigint,
	evt bigint,
	gid bigint NOT NULL,
	hs bigint,
	locX bigint,
	locY bigint,
	mid bigint,
	mtype bigint,
	oftid bigint,
	opid varchar(255),
	opt1 bigint,
	opt2 bigint,
	ord float,
	period bigint,
	pid bigint NOT NULL,
	tid bigint NOT NULL,
	vs bigint,
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (gid, tid)
);


CREATE TABLE IF NOT EXISTS PlayerGameSummary(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	ast bigint,
	blk bigint,
	blka bigint,
	court bigint,
	dreb bigint,
	fbpts bigint,
	fbptsa bigint,
	fbptsm bigint,
	fga bigint,
	fgm bigint,
	fn varchar(255),
	fta bigint,
	ftm bigint,
	gid bigint NOT NULL,
	ln varchar(255),
	memo varchar(255),
	mid bigint,
	min bigint,
	num varchar(255),
	oreb bigint,
	pf bigint,
	pid bigint NOT NULL,
	pip bigint,
	pipa bigint,
	pipm bigint,
	pm bigint,
	pos varchar(255),
	pts bigint,
	reb bigint,
	sec bigint,
	status varchar(255),
	stl bigint,
	ta varchar(255),
	tf bigint,
	tid bigint NOT NULL,
	totsec bigint,
	tov bigint,
	tpa bigint,
	tpm bigint,
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (gid),
    INDEX (tid),
    INDEX (pid)
);


CREATE TABLE IF NOT EXISTS Players(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	PlayerID bigint NOT NULL,
	FirstName varchar(255),
	LastName varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS Teams(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	TeamID bigint NOT NULL,
	TeamCode varchar(255),
	TeamLogo varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
UPDATE  Teams
SET TeamLogo = IF(LENGTH(TeamID)=(10), 'https://stats.nba.com/media/img/teams/logos/'+TeamCode+'_logo.svg','');


CREATE TABLE IF NOT EXISTS TeamRosters(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	TeamID varchar(255),
	SEASON varchar(255),
	LeagueID varchar(255),
	PLAYER varchar(255),
	NUM varchar(255),
	POSITION varchar(255),
	HEIGHT varchar(255),
	WEIGHT varchar(255),
	BIRTH_DATE varchar(255),
	AGE varchar(255),
	EXP varchar(255),
	SCHOOL varchar(255),
	PLAYER_ID varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS DRAFTHISTORY(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	TEAM_CITY varchar(255),
	TEAM_ID varchar(255),
	PERSON_ID varchar(255),
	DRAFT_TYPE varchar(255),
	ROUND_PICK varchar(255),
	ORGANIZATION varchar(255),
	TEAM_NAME varchar(255),
	OVERALL_PICK varchar(255),
	PLAYER_NAME varchar(255),
	SEASON varchar(255),
	ROUND_NUMBER varchar(255),
	TEAM_ABBREVIATION varchar(255),
	ORGANIZATION_TYPE varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS DRILLRESULTS(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	LAST_NAME varchar(255),
	STANDING_VERTICAL_LEAP varchar(255),
	LANE_AGILITY_TIME varchar(255),
	PLAYER_NAME varchar(255),
	PLAYER_ID varchar(255),
	MODIFIED_LANE_AGILITY_TIME varchar(255),
	BENCH_PRESS varchar(255),
	SeasonYear varchar(255),
	TEMP_PLAYER_ID varchar(255),
	POSITION varchar(255),
	MAX_VERTICAL_LEAP varchar(255),
	THREE_QUARTER_SPRINT varchar(255),
	FIRST_NAME varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS NONSTATIONARYSHOOTING(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	OFF_DRIB_FIFTEEN_BREAK_RIGHT_ATTEMPT varchar(255),
	OFF_DRIB_COLLEGE_BREAK_RIGHT_ATTEMPT varchar(255),
	OFF_DRIB_COLLEGE_BREAK_LEFT_MADE varchar(255),
	ON_MOVE_FIFTEEN_PCT varchar(255),
	PLAYER_ID varchar(255),
	OFF_DRIB_FIFTEEN_BREAK_RIGHT_MADE varchar(255),
	OFF_DRIB_COLLEGE_BREAK_LEFT_ATTEMPT varchar(255),
	OFF_DRIB_COLLEGE_TOP_KEY_MADE varchar(255),
	OFF_DRIB_FIFTEEN_BREAK_RIGHT_PCT varchar(255),
	OFF_DRIB_COLLEGE_BREAK_LEFT_PCT varchar(255),
	FIRST_NAME varchar(255),
	OFF_DRIB_COLLEGE_TOP_KEY_ATTEMPT varchar(255),
	SeasonYear varchar(255),
	TEMP_PLAYER_ID varchar(255),
	ON_MOVE_FIFTEEN_MADE varchar(255),
	OFF_DRIB_COLLEGE_BREAK_RIGHT_MADE varchar(255),
	OFF_DRIB_FIFTEEN_BREAK_LEFT_PCT varchar(255),
	OFF_DRIB_COLLEGE_BREAK_RIGHT_PCT varchar(255),
	LAST_NAME varchar(255),
	OFF_DRIB_FIFTEEN_BREAK_LEFT_ATTEMPT varchar(255),
	ON_MOVE_FIFTEEN_ATTEMPT varchar(255),
	OFF_DRIB_FIFTEEN_BREAK_LEFT_MADE varchar(255),
	ON_MOVE_COLLEGE_PCT varchar(255),
	PLAYER_NAME varchar(255),
	ON_MOVE_COLLEGE_MADE varchar(255),
	OFF_DRIB_FIFTEEN_TOP_KEY_MADE varchar(255),
	POSITION varchar(255),
	OFF_DRIB_FIFTEEN_TOP_KEY_ATTEMPT varchar(255),
	ON_MOVE_COLLEGE_ATTEMPT varchar(255),
	OFF_DRIB_COLLEGE_TOP_KEY_PCT varchar(255),
	OFF_DRIB_FIFTEEN_TOP_KEY_PCT varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS PLAYERANTHRO(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	WINGSPAN_FT_IN varchar(255),
	PLAYER_ID varchar(255),
	HEIGHT_W_SHOES_FT_IN varchar(255),
	WINGSPAN varchar(255),
	HEIGHT_W_SHOES varchar(255),
	STANDING_REACH_FT_IN varchar(255),
	FIRST_NAME varchar(255),
	HAND_WIDTH varchar(255),
	SeasonYear varchar(255),
	TEMP_PLAYER_ID varchar(255),
	WEIGHT varchar(255),
	LAST_NAME varchar(255),
	HAND_LENGTH varchar(255),
	HEIGHT_WO_SHOES_FT_IN varchar(255),
	HEIGHT_WO_SHOES varchar(255),
	BODY_FAT_PCT varchar(255),
	PLAYER_NAME varchar(255),
	STANDING_REACH varchar(255),
	`POSITION` varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS SPOTSHOOTING(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	FIFTEEN_CORNER_LEFT_MADE varchar(255),
	COLLEGE_CORNER_LEFT_PCT varchar(255),
	NBA_TOP_KEY_PCT varchar(255),
	PLAYER_ID varchar(255),
	NBA_BREAK_RIGHT_ATTEMPT varchar(255),
	COLLEGE_TOP_KEY_PCT varchar(255),
	NBA_BREAK_RIGHT_PCT varchar(255),
	NBA_BREAK_LEFT_PCT varchar(255),
	COLLEGE_CORNER_LEFT_MADE varchar(255),
	FIFTEEN_BREAK_RIGHT_ATTEMPT varchar(255),
	FIRST_NAME varchar(255),
	NBA_CORNER_RIGHT_MADE varchar(255),
	NBA_CORNER_LEFT_PCT varchar(255),
	FIFTEEN_BREAK_LEFT_ATTEMPT varchar(255),
	FIFTEEN_BREAK_LEFT_PCT varchar(255),
	SeasonYear varchar(255),
	TEMP_PLAYER_ID varchar(255),
	FIFTEEN_BREAK_RIGHT_PCT varchar(255),
	FIFTEEN_CORNER_LEFT_PCT varchar(255),
	COLLEGE_CORNER_RIGHT_PCT varchar(255),
	NBA_TOP_KEY_ATTEMPT varchar(255),
	COLLEGE_CORNER_RIGHT_ATTEMPT varchar(255),
	NBA_BREAK_LEFT_ATTEMPT varchar(255),
	FIFTEEN_BREAK_RIGHT_MADE varchar(255),
	LAST_NAME varchar(255),
	FIFTEEN_TOP_KEY_PCT varchar(255),
	FIFTEEN_TOP_KEY_ATTEMPT varchar(255),
	FIFTEEN_CORNER_RIGHT_ATTEMPT varchar(255),
	FIFTEEN_BREAK_LEFT_MADE varchar(255),
	COLLEGE_BREAK_RIGHT_PCT varchar(255),
	NBA_TOP_KEY_MADE varchar(255),
	FIFTEEN_CORNER_LEFT_ATTEMPT varchar(255),
	COLLEGE_BREAK_LEFT_PCT varchar(255),
	COLLEGE_TOP_KEY_ATTEMPT varchar(255),
	NBA_CORNER_LEFT_ATTEMPT varchar(255),
	NBA_BREAK_LEFT_MADE varchar(255),
	COLLEGE_CORNER_LEFT_ATTEMPT varchar(255),
	FIFTEEN_TOP_KEY_MADE varchar(255),
	NBA_CORNER_RIGHT_PCT varchar(255),
	COLLEGE_TOP_KEY_MADE varchar(255),
	NBA_BREAK_RIGHT_MADE varchar(255),
	PLAYER_NAME varchar(255),
	NBA_CORNER_LEFT_MADE varchar(255),
	COLLEGE_BREAK_RIGHT_MADE varchar(255),
	`POSITION` varchar(255),
	FIFTEEN_CORNER_RIGHT_PCT varchar(255),
	COLLEGE_BREAK_LEFT_MADE varchar(255),
	COLLEGE_BREAK_LEFT_ATTEMPT varchar(255),
	NBA_CORNER_RIGHT_ATTEMPT varchar(255),
	COLLEGE_BREAK_RIGHT_ATTEMPT varchar(255),
	COLLEGE_CORNER_RIGHT_MADE varchar(255),
	FIFTEEN_CORNER_RIGHT_MADE varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS STATS(
    Id INT AUTO_INCREMENT PRIMARY KEY,
	WINGSPAN_FT_IN varchar(255),
	PLAYER_ID varchar(255),
	HEIGHT_W_SHOES_FT_IN varchar(255),
	WINGSPAN varchar(255),
	HEIGHT_W_SHOES varchar(255),
	STANDING_REACH_FT_IN varchar(255),
	FIRST_NAME varchar(255),
	SEASON varchar(255),
	HAND_WIDTH varchar(255),
	LANE_AGILITY_TIME varchar(255),
	MODIFIED_LANE_AGILITY_TIME varchar(255),
	BENCH_PRESS varchar(255),
	SeasonYear varchar(255),
	WEIGHT varchar(255),
	LAST_NAME varchar(255),
	HAND_LENGTH varchar(255),
	HEIGHT_WO_SHOES_FT_IN varchar(255),
	HEIGHT_WO_SHOES varchar(255),
	MAX_VERTICAL_LEAP varchar(255),
	BODY_FAT_PCT varchar(255),
	STANDING_VERTICAL_LEAP varchar(255),
	PLAYER_NAME varchar(255),
	STANDING_REACH varchar(255),
	`POSITION` varchar(255),
	THREE_QUARTER_SPRINT varchar(255),
	LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
