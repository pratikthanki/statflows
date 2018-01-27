import mysql.connector
import simplejson as json
from marshmallow import Schema
from sqlalchemy.ext.declarative import as_declarative

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask import Flask, request, jsonify
from flask import jsonify
from flask.views import View

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://myuser:mypwd@host/dbname"

db = SQLAlchemy(app)

# test class
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world!'}

api.add_resource(HelloWorld, '/')



class Players(db.Model):
    __tablename__ = 'Players'
    PlayerID = db.Column(db.Integer, primary_key=True, nullable=False)
    LastName = db.Column(db.String(20))
    FirstName = db.Column(db.String(20))


class Teams(db.Model):
    __tablename__ = 'Teams'
    TeamID  = db.Column(db.Integer, primary_key=True, nullable=False)
    TeamCode = db.Column(db.Text)


class Games(db.Model):
    __tablename__ = 'Games'
    GameID = db.Column(db.Integer, primary_key=True, nullable=False)
    Venue = db.Column(db.String(50))
    GameCode = db.Column(db.String(30), nullable=False)
    DateString = db.Column(db.String(10), nullable=False)
    Date = db.Column(db.DateTime, nullable=False)


class PlayerGameSummary(db.Model):
    __tablename__ = 'PlayerGameSummary'
    Ast = db.Column(db.Integer)
    Blk = db.Column(db.Integer)
    Blka = db.Column(db.Integer)
    Court = db.Column(db.Integer)
    Dreb = db.Column(db.Integer)
    Fbpts = db.Column(db.Integer)
    Fbptsa = db.Column(db.Integer)
    Fbptsm = db.Column(db.Integer)
    Fga = db.Column(db.Integer)
    Fgm = db.Column(db.Integer)
    Fn = db.Column(db.Text)
    Fta = db.Column(db.Integer)
    Ftm = db.Column(db.Integer)
    GameID = db.Column(db.Integer, primary_key=True, nullable=False)
    Ln = db.Column(db.Text)
    Memo = db.Column(db.Text)
    Mid = db.Column(db.Integer)
    Min = db.Column(db.Integer)
    Num = db.Column(db.Text)
    Oreb = db.Column(db.Integer)
    Pf = db.Column(db.Integer)
    PlayerID = db.Column(db.Integer, primary_key=True, nullable=False)
    Pip = db.Column(db.Integer)
    Pipa = db.Column(db.Integer)
    Pipm = db.Column(db.Integer)
    Pm = db.Column(db.Integer)
    Pos = db.Column(db.Text)
    Pts = db.Column(db.Integer)
    Reb = db.Column(db.Integer)
    Sec = db.Column(db.Integer)
    Status = db.Column(db.Text)
    Stl = db.Column(db.Integer)
    Ta = db.Column(db.Text)
    Tf = db.Column(db.Integer)
    TeamID = db.Column(db.Integer, nullable=False)
    Totsec = db.Column(db.Integer)
    Tov = db.Column(db.Integer)
    Tpa = db.Column(db.Integer)
    Tpm = db.Column(db.Integer)
    Id = db.Column(db.Text)



class GamePlays(db.Model):
    __tablename__ = 'GamePlays'
    ClockTime = db.Column(db.Text)
    Description = db.Column(db.Text)
    EPId = db.Column(db.Text)
    EType = db.Column(db.Integer)
    Evt = db.Column(db.Integer)
    GameID = db.Column(db.Integer, primary_key=True, nullable=False)
    HS = db.Column(db.Integer)
    LocationX = db.Column(db.Integer)
    LocationY = db.Column(db.Integer)
    MId = db.Column(db.Integer)
    MType = db.Column(db.Integer)
    OftId = db.Column(db.Integer)
    OpId = db.Column(db.Text)
    Opt1 = db.Column(db.Integer, primary_key=True, nullable=False)
    Opt2 = db.Column(db.Integer)
    Ord = db.Column(db.Integer)
    Period = db.Column(db.Integer)
    PlayerID = db.Column(db.Integer, primary_key=True, nullable=False)
    TeamID = db.Column(db.Integer, primary_key=True, nullable=False)
    Vs = db.Column(db.Integer)
    Id = db.Column(db.Text)



# We use marshmallow Schema to serialize our database records
class PlayersSchema(Schema):
    class Meta:
        fields = ('PlayerID', 'LastName', 'FirstName')



class TeamsSchema(Schema):
    class Meta:
        fields = ('TeamID', 'TeamCode')



class GamesSchema(Schema):
    class Meta:
        fields = ('GameID', 'Date', 'DateString', 'GameCode', 'Venue')



class PlayerGameSummarySchema(Schema):
    class Meta:
        fields = ('Ast', 'Blk', 'Blka', 'Court', 'Dreb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fn', 'Fta', 'Ftm', 'GameID', 'Ln', 'Memo', 'Mid', 'Min', 'Num', 'Oreb', 'Pf', 'PlayerID', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pos', 'Pts', 'Reb', 'Sec', 'Status', 'Stl', 'Ta', 'Tf', 'TeamID', 'Totsec', 'Tov', 'Tpa', 'Tpm', 'Id')



class GamePlaysSchema(Schema):
    class Meta:
        fields = ('ClockTime', 'Description', 'EPId', 'EType', 'Evt', 'GameID', 'HS', 'LocationX', 'LocationY', 'MId', 'MType', 'OftId', 'OpId', 'Opt1', 'Opt2', 'Ord', 'Period', 'PlayerID', 'TeamID', 'Vs', 'Id')



players_schema = PlayersSchema()                
many_players_schema = PlayersSchema(many=True)  
class players_call():
    @app.route('/api/players/', methods=['GET'])
    def players_query(PlayerID = None):
        if PlayerID:
            item = Players.query.get(PlayerID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(PlayerID)]}), 404
            else:
                result = players_schema.dump(item)  
                return jsonify(result.data)  
        else:
            items = Players.query.all() 
            result = many_players_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/players/<int:player_id>', methods=['GET'])
    def player_filter_query(player_id):
        item = Players.query.filter_by(PlayerID=player_id)
        result = many_players_schema.dump(item)  
        return jsonify(result.data)



teams_schema = TeamsSchema()                
many_teams_schema = TeamsSchema(many=True)  
class teams_call():
    @app.route('/api/teams/', methods=['GET'])
    def teams_query(TeamID = None):
        if TeamID:
            item = Teams.query.get(TeamID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(TeamID)]}), 404
            else:
                result = teams_schema.dump(item)  
                return jsonify(result.data)  
        else:
            items = Teams.query.all() 
            result = many_teams_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/teams/<int:team_id>', methods=['GET'])
    def team_filter_query(team_id):
        item = Teams.query.filter_by(TeamID=team_id)
        result = many_teams_schema.dump(item)  
        return jsonify(result.data)

 

games_schema = GamesSchema()               
many_games_schema = GamesSchema(many=True) 
class games_query():
    @app.route('/api/games/', methods=['GET'])
    def games_query(GameID = None):
        if GameID:
            item = Games.query.get(GameID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(GameID)]}), 404
            else:
                result = games_schema.dump(item)  
                return jsonify(result.data)  
        else:
            items = Games.query.all() 
            result = many_games_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/games/<int:game_id>', methods=['GET'])
    def game_filter_query(game_id):
        item = Games.query.filter_by(GameID=game_id)
        result = many_games_schema.dump(item)  
        return jsonify(result.data)



gamestats_schema = PlayerGameSummarySchema()               
many_gamestats_schema = PlayerGameSummarySchema(many=True)  
class gamestats_query():
    @app.route('/api/games/stats/', methods=['GET'])
    def gamestats_query(GameID = None):
        if GameID:
            item = PlayerGameSummary.query.with_entities(PlayerGameSummary.GameID)
            item = item.distinct()
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(GameID)]}), 404
            else:
                result = gamestats_schema.dump(item)  
                return jsonify(result.data)  
        else:
            items = PlayerGameSummary.query.with_entities(PlayerGameSummary.GameID)
            items = items.distinct()
            result = many_gamestats_schema.dump(items)
            return jsonify(result.data)


    @app.route('/api/games/stats/<int:game_id>', methods=['GET'])
    def gamestats_filter_query(game_id):
        item = PlayerGameSummary.query.filter_by(GameID=game_id)
        result = many_gamestats_schema.dump(item)
        return jsonify(result.data)



gameplays_schema = GamePlaysSchema()               
many_gameplays_schema = GamePlaysSchema(many=True) 
class gamestats_query():
    @app.route('/api/games/plays/', methods=['GET'])
    def gameplays_query(GameID = None):
        if GameID:
            item = GamePlays.query.with_entities(GamePlays.GameID)
            item = item.distinct()
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(GameID)]}), 404
            else:
                result = gameplays_schema.dump(item)  
                return jsonify(result.data)  
        else:
            items = GamePlays.query.with_entities(GamePlays.GameID)
            items = items.distinct()
            result = many_gameplays_schema.dump(items)
            return jsonify(result.data)


    @app.route('/api/games/plays/<int:game_id>', methods=['GET'])
    def gameplays_filter_query(game_id):
        item = GamePlays.query.filter_by(GameID=game_id)
        result = many_gameplays_schema.dump(item)
        return jsonify(result.data)


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(600)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    app.config['SQLALCHEMY_ECHO'] = True  # Show SQL commands created
    app.run()
