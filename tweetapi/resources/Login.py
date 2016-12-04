#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import random

import flask_restful as  restful
from flask_restful import reqparse
from flask import request, g
from tweetapi.database import db, User
from tweetapi.resources import users, generate_token


class Login(restful.Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']
        token, user_id = self.login(username, password)
        if token is not None:
            return {'token':token, 'user_id':user_id}
        else:
            return {'error':'invalid username or password'}, 400
        pass

    def login(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and user.password == password:
            token = generate_token(user.user_id)
            users[token] = user.user_id
            return token, user.user_id

        else:
            return None, None
        pass


class Logout(restful.Resource):
    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('user_id', type=int, required=True, location=['json', 'args'])
        self.post_parse.add_argument('Authorization', type=unicode, required=True, location='headers')

    def post(self):
        token = self.post_parse.parse_args()['Authorization']
        print token
        users.pop(token.split(' ', 1)[1])
        return {'message': 'logout success'}



