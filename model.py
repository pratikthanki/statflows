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

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://uid:pwd@host/dbname"

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



players_schema = PlayersSchema()                # Single object
many_players_schema = PlayersSchema(many=True)  # List of objects
class players_call():
    @app.route('/api/players/', methods=['GET'])
    def players_query(PlayerID = None):
        if PlayerID:
            item = Players.query.get(PlayerID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(PlayerID)]}), 404
            else:
                result = players_schema.dump(item)  # Serialize object
                return jsonify(result.data)  # Uses simplejson 
        else:
            items = Players.query.all() 
            result = many_players_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/players/<int:player_id>', methods=['GET'])
    def player_filter_query(player_id):
        item = Players.query.filter_by(PlayerID=player_id)
        result = many_players_schema.dump(item)  
        return jsonify(result.data)



teams_schema = TeamsSchema()                # Single object
many_teams_schema = TeamsSchema(many=True)  # List of objects
class teams_call():
    @app.route('/api/teams/', methods=['GET'])
    def teams_query(TeamID = None):
        if TeamID:
            item = Teams.query.get(TeamID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(TeamID)]}), 404
            else:
                result = teams_schema.dump(item)  # Serialize object
                return jsonify(result.data)  # Uses simplejson 
        else:
            items = Teams.query.all() 
            result = many_teams_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/teams/<int:team_id>', methods=['GET'])
    def team_filter_query(team_id):
        item = Teams.query.filter_by(TeamID=team_id)
        result = many_teams_schema.dump(item)  
        return jsonify(result.data)

 

games_schema = GamesSchema()               # Single object
many_games_schema = GamesSchema(many=True)  # List of objects
class games_query():
    @app.route('/api/games/', methods=['GET'])
    def games_query(GameID = None):
        if GameID:
            item = Games.query.get(GameID)
            if item is None:
                return jsonify({'err_msg': ["We could not find item '{}'".format(GameID)]}), 404
            else:
                result = games_schema.dump(item)  # Serialize object
                return jsonify(result.data)  # Uses simplejson 
        else:
            items = Games.query.all() 
            result = many_games_schema.dump(items)  
            return jsonify(result.data)


    @app.route('/api/games/<int:game_id>', methods=['GET'])
    def game_filter_query(game_id):
        item = Games.query.filter_by(GameID=game_id)
        result = many_games_schema.dump(item)  
        return jsonify(result.data)



if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = int(600)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
    app.config['SQLALCHEMY_ECHO'] = True  # Show SQL commands created
    app.run()
