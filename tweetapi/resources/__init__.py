import time, base64
from flask_restful import fields
from flask import make_response, jsonify, g, request
from flask_httpauth import HTTPTokenAuth

user_fields = {
    'username': fields.String,
    'user_id': fields.Integer,
    'photo_url': fields.String
}

tweet_fields = {
    'user': fields.Nested(user_fields),
    'description': fields.String,
    'likes': fields.Boolean,
    'tweet_id': fields.Integer,
    'image_url':fields.String
}

comment_fields = {
    'user': fields.Nested(user_fields),
    'tweet_id': fields.String,
    'to_user_id': fields.Integer,
    'content': fields.String
}

auth = HTTPTokenAuth(scheme='Token')
users = {
    "aaabbbccc": "john",
    "bbbcccddd": "susan"
}


@auth.verify_token
def verify_token(token):
    if token in users:
        if request.method == 'GET':
            return True
        data = request.json
        if 'user_id' in data and data['user_id'] == users[token]:
            return True
    return False


@auth.error_handler
def unauthorized():
    resp = make_response(jsonify({'error': 'Unauthorized access'}), 401)
    return resp


def generate_token(user_id):
    string = unicode(user_id)+':'+unicode(time.time())
    return base64.b64encode(string)


def parse_token(token):
    string = base64.b64decode(token)
    user_id, login_time = string.split(':')
    return int(user_id)