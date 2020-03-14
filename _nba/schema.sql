
CREATE TABLE games
(
	game_id varchar(50) NULL,
	game_code varchar(50) NULL,
	venue varchar(50) NULL,
	date varchar(10) NULL,
	away_team_id bigint NULL,
	away_score int NULL,
	home_team_id bigint NULL,
	home_score int NULL,
	season varchar(10) NULL,
    LastUpdated timestamp NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE TABLE game_pbp
(
    game_pbp_id int GENERATED ALWAYS AS IDENTITY,
    cl varchar(10) NULL,
    de varchar(255) NULL,
    epid bigint NULL,
    etype bigint NULL,
    evt bigint NULL,
    gid varchar(50) NOT NULL,
    hs bigint NULL,
    locX bigint NULL,
    locY bigint NULL,
    mid bigint NULL,
    mtype bigint NULL,
    oftid bigint NULL,
    opid bigint NULL,
    opt1 bigint NULL,
    opt2 bigint NULL,
    ord float NULL,
    period bigint NULL,
    pid bigint NOT NULL,
    tid bigint NOT NULL,
    vs bigint NULL,
    LastUpdated timestamp NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE TABLE game_stats
(
    game_stats_id int GENERATED ALWAYS AS IDENTITY,
	ast bigint NULL,
	blk bigint NULL,
	blka bigint NULL,
	court bigint NULL,
	dreb bigint NULL,
	fbpts bigint NULL,
	fbptsa bigint NULL,
	fbptsm bigint NULL,
	fga bigint NULL,
	fgm bigint NULL,
	fn varchar(30) NULL,
	fta bigint NULL,
	ftm bigint NULL,
	gid varchar(50) NOT NULL,
	ln varchar(30) NULL,
	memo varchar(100) NULL,
	mid bigint NULL,
	min bigint NULL,
	num varchar(3) NULL,
	oreb bigint NULL,
	pf bigint NULL,
	pid bigint NOT NULL,
	pip bigint NULL,
	pipa bigint NULL,
	pipm bigint NULL,
	pm bigint NULL,
	pos varchar(10) NULL,
	pts bigint NULL,
	reb bigint NULL,
	sec bigint NULL,
	status varchar(2) NULL,
	stl bigint NULL,
	ta varchar(5) NULL,
	tf bigint NULL,
	tid bigint NOT NULL,
	totsec bigint NULL,
	tov bigint NULL,
	tpa bigint NULL,
	tpm bigint NULL,
    LastUpdated timestamp NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE TABLE teams
(
	team_id bigint NOT NULL,
	team_code varchar(255) NULL,
	LastUpdated timestamp NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE TABLE rosters
(
	teamid varchar(255) NULL,
	season varchar(255) NULL,
	leagueid varchar(255) NULL,
	player varchar(255) NULL,
	num varchar(255) NULL,
	position varchar(255) NULL,
	height varchar(255) NULL,
	weight varchar(255) NULL,
	birth_date varchar(255) NULL,
	age varchar(255) NULL,
	exp varchar(255) NULL,
	school varchar(255) NULL,
	player_id varchar(255) NULL,
	LastUpdated timestamp NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);
