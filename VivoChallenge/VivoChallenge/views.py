"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from VivoChallenge import app
from flask_restful import Resource, Api
from flask import request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import requests
import uuid

api = Api(app)

def existeBot(arg):
    return existeDb(arg)

def existeMensagem(arg):
    return existeDbMsg(arg)

if __name__ == '__main__':
    app.run(debug=True)

user, password = 'root', '123456'
host = 'localhost'
dbase = 'vivochallenge'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(user, password, host, dbase)
db = SQLAlchemy(app)

class Bot(db.Model):
    __tablename__ = "bot"
    id = db.Column(db.String(16), primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    conversationId = db.Column(db.String(36), nullable=False)
    timestamp = db.Column(db.String(45), nullable=False)
    from_ = db.Column(db.String(36), nullable=False)
    to = db.Column(db.String(36), nullable=False)
    text = db.Column(db.String(255), nullable=False)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        return super(DateTimeEncoder, self).default(obj)

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and x != 'query' and x != 'query_class']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    if field == 'creationDate':
                        data = obj.__getattribute__(field)
                        data = str(data)
                    fields[field] = data
                except TypeError:
                    if field == 'creationDate':
                        data = obj.__getattribute__(field)
                        data = str(data)
                        fields[field] = data
                    else:
                        fields[field] = None
            return fields

        return json.JSONEncoder.default(self, obj)


def addBotDb(details):
    id_ = details['id']
    name_ = details['name']
    theBot = Bot(id=id_, name=name_)
    db.session.add(theBot)
    db.session.commit()

def addMsgDb(details):
    id_ = str(uuid.uuid4())
    conversationId_ = details['conversationId']
    timestamp_ = details['timestamp']
    from__ = details['from']
    to_ = details['to']
    text_ = details['text']
    theMessage = Message(id=id_, 
                         conversationId=conversationId_,
                         timestamp = timestamp_,
                         from_ = from__,
                         to = to_,
                         text = text_)
    db.session.add(theMessage)
    db.session.commit()

def updateBotDb(details):
    id_ = details['id']
    name_ = details['name']
    theBot = db.session.query(Bot).get(id_)
    theBot.name = name_
    db.session.commit()

def existeDb(details):
    existe = False
    id_ = details
    theBot = db.session.query(Bot).get(id_)
    if theBot != None:
        existe = True
    return existe

def existeDbMsg(details):
    existe = False
    id_ = details
    theMsg = db.session.query(Message).get(id_)
    if theMsg != None:
        existe = True
    return existe

def getDbConversation(details):
    id_ = details
    msgs = db.session.query(Message).filter(Message.conversationId == id_).all()
    return msgs

def getDb(details):
    id_ = details
    theBot = db.session.query(Bot).get(id_)
    return theBot

def getDbMsg(details):
    id_ = details
    theMsg = db.session.query(Message).get(id_)
    return theMsg

def deleteDb(details):
    theBot = db.session.query(Bot).get(details)
    db.session.delete(theBot)
    db.session.commit()
    return None


class BotsSpecific(Resource):
    # return specific resources
    # 200 
    def get(self, bot_id):
        bot = getDb(bot_id)
        status_code = 200
        return json.dumps(bot, cls=AlchemyEncoder), status_code

    # delete a resource
    # 204 No Content
    def delete(self, bot_id):
        data = request.get_json()
        bot_id = data['id']
        status_code = 200
        retorno = {'bots':'Ok!'}
        if existeBot(bot_id):
            deleteDb(bot_id)
            retorno = {'bots':'Removed!'}
            status_code = 204
        return retorno, status_code

class Bots(Resource):
    # insert a new resource
    # 201 Created, 200 Ok
    def post(self):
        data = request.get_json()
        bot_id = data['id']
        retorno = {'bots':'Ok!'}
        status_code = 200
        if existeBot(bot_id) == False:
            addBotDb(data)
            status_code = 201
            retorno = {'bots':'Created!'}
        return retorno, status_code

    # update or insert a new resource
    # 200 
    def put(self):
        data = request.get_json()
        bot_id = data['id']
        retorno = {'bots':'Ok!'}
        status_code = 200
        if existeBot(bot_id) == False:
            addBotDb(data)
            status_code = 201
            retorno = {'bots':'Created!'}
        else:
            updateBotDb(data)
            status_code = 200
            retorno = {'bots':'Updated!'}
        return retorno, status_code

    # return resources
    # 200 
    def get(self):
        allBots = Bot.query.all()
        return json.dumps(allBots, cls=AlchemyEncoder), 200

    
class Messages(Resource):
    def get(self):
        cid = request.args.get('conversationId')
        allMsg = None
        if cid == None:
            allMsg = {}
        else:
            allMsg = getDbConversation(cid)
        return json.dumps(allMsg, cls=AlchemyEncoder), 200

    def post(self):
        data = request.get_json()
        retorno = {'message':'Ok!'}
        status_code = 200
        if existeMensagem(id) == False:
            try:
                addMsgDb(data)
                status_code = 201
                retorno = {'message':'Created!'}
            except:
                status_code = 200
                retorno = {'message':'Not created!', 'error':'Bot not registered. Try to create the bot first.'}
        return retorno, status_code


class MessagesSpecific(Resource):
    def get(self, msg_id):
        msg = getDbMsg(msg_id)
        status_code = 200
        return json.dumps(msg, cls=AlchemyEncoder), status_code


api.add_resource(Bots,             '/api/v1/bots')
api.add_resource(BotsSpecific,     '/api/v1/bots/<string:bot_id>')
api.add_resource(Messages,         '/api/v1/messages')
api.add_resource(MessagesSpecific, '/api/v1/messages/<string:msg_id>')

@app.route('/')
def default():
    return "<h3>Vivo Challenge - The Bot API</h3>"

@app.route('/exemplo')
def summary():
    bots = Bot.query.all()
    return json.dumps(bots, cls=AlchemyEncoder)