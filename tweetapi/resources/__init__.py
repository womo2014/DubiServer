from flask_restful import fields
from flask import Flask, make_response, jsonify
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
tokens = {
    "aaabbbccc": "john",
    "bbbcccddd": "susan"
}


@auth.verify_token
def verify_token(token):
    print token
    if token in tokens:
        # g.current_user = tokens[token]
        return True
    return False


@auth.error_handler
def unauthorized():
    resp = make_response(jsonify({'error': 'Unauthorized access'}), 401)
    return resp

