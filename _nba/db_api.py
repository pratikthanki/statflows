from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from teams import TEAMS
from nba_settings import player_img_url, team_img_url
from shared_modules import create_logger, MongoConnection

app = Flask(__name__)

projects = ['match-stats', 'match-pbp']
mongodb_connector = MongoConnection(project=projects[0])
nba_db = mongodb_connector.db_connect('nba')

STATS_COLUMNS = ["fn", "ln", "num", "pos", "min", "sec", "totsec", "fga", "fgm", "tpa", "tpm", "fta", "ftm",
                 "oreb", "dreb", "reb", "ast", "stl", "blk", "pf", "pts", "tov", "fbpts", "fbptsa", "fbptsm",
                 "pip", "pipa", "pipm", "court", "pid", "pm", "blka", "tf", "status", "gid", "mid", "tid", "ta"]


def query_roster():
    output = []
    for s in nba_db.roster.find():
        team_id = str(s['TeamID'])
        output.append({
            'TeamId': s['TeamID'],
            'Season': s['SEASON'],
            'LeagueId': s['LeagueID'],
            'PlayerName': s['PLAYER'],
            'Num': s['NUM'],
            'Position': s['POSITION'],
            'Height': s['HEIGHT'],
            'Weight': s['WEIGHT'],
            'BirthDate': s['BIRTH_DATE'],
            'Age': s['AGE'],
            'Experience': s['EXP'],
            'School': s['SCHOOL'],
            'PlayerId': s['PLAYER_ID'],
            'LastUpdated': s['LAST_UPDATED'],
            'TeamLogo': team_img_url.format(TEAMS[team_id]['displayAbbr']),
            'PlayerIme': player_img_url.format(s['PLAYER_ID']),
            'Division': TEAMS[team_id]['division'],
            'Conference': TEAMS[team_id]['conference']
        })

    last_updated = max([row['LastUpdated'] for row in output])
    roster = [row for row in output if row['LastUpdated'] == last_updated]

    return roster


def get_game_info(game_id):
    for row in nba_db.games.find({'game_id': game_id}):
        return {
            "game_id": row['game_id'],
            "game_code": row['game_code'],
            "venue": row['venue'],
            "date": row['date'],
            "date_string": row['date_string'],
            "away_team_id": row['away_team_id'],
            "away_score": row['away_score'],
            "home_team_id": row['home_team_id'],
            "home_score": row['home_score'],
        }


@app.route('/api/roster', methods=['GET'])
def get_roster():
    roster = query_roster()

    return jsonify(roster)


@app.route('/api/stats', methods=['GET'])
def get_latest_stats():
    roster = query_roster()

    output = []
    for s in nba_db.match_stats.find({'tid': 1610612744, 'pid': 201939}):
        game_meta = get_game_info(str(s['gid']))
        row = {metric: s[metric] for metric in STATS_COLUMNS}
        row['date'] = game_meta['date']

        output.append(row)

    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
