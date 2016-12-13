import threading
import time, base64
from flask_restful import fields
from flask import make_response, jsonify, g, request
from flask_httpauth import HTTPTokenAuth
from tweetapi.database import User
from tweetapi.globals import users, mutex
user_fields = {
    'username': fields.String,
    'user_id': fields.Integer,
    'photo_url': fields.String
}

tweet_fields = {
    'user': fields.Nested(user_fields),
    # 'user_id': fields.Integer,
    'time': fields.DateTime,
    'description': fields.String,
    'likes': fields.Integer,
    'tweet_id': fields.Integer,
    'image_url':fields.String
}

comment_fields = {
    'comment_id': fields.Integer,
    'tweet_id': fields.Integer,
    'from_user_id': fields.Integer,
    'to_user_id': fields.Integer,
    'content': fields.String,
    'time': fields.DateTime,
}

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    print 'token:', token
    mutex.acquire()
    is_logged = token in users
    mutex.release()
    if is_logged:
        g.user = User.query.get(parse_token(token))
        print g.user
        if g.user is not None:
            return True
    g.msg = ' token:'+ token
    return False


@auth.error_handler
def unauthorized():
    resp = make_response(jsonify({'message': 'Unauthorized access' + g.msg}), 401)
    return resp


def generate_token(user_id):
    string = unicode(user_id)+':'+unicode(time.time())
    return base64.b64encode(string)


def parse_token(token):
    string = base64.b64decode(token)
    user_id, login_time = string.split(':')
    return int(user_id)