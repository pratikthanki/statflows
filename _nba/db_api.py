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


@app.route('/api/roster', methods=['GET'])
def get_roster():
    output = []
    for s in nba_db.roster.find():
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
            'TeamLogo': team_img_url.format(TEAMS[str(s['TeamID'])]['displayAbbr']),
            'PlayerIme': player_img_url.format(s['PLAYER_ID']),
            'Division': TEAMS[str(s['TeamID'])]['division'],
            'Conference': TEAMS[str(s['TeamID'])]['conference']
        })

    last_updated = max([row['LastUpdated'] for row in output])
    roster = [row for row in output if row['LastUpdated'] == last_updated]

    return jsonify(roster)


@app.route('/api/stats', methods=['GET'])
def get_latest_stats():
    return jsonify(TEAMS)


if __name__ == '__main__':
    app.run(debug=True)
