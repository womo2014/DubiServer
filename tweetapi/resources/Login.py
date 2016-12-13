#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import random

import flask_restful as  restful
from flask_restful import reqparse
from flask import request, g
from tweetapi.database import db, User, LoginInfo
from tweetapi.resources import  generate_token
from tweetapi import global_vars


class Login(restful.Resource):
    def post(self):
        data = request.form
        username = data['username']
        password = data['password']
        token, user_id = self.login(username, password)
        if token is not None:
            return {'token':token, 'user_id':user_id}
        else:
            return {'message':'invalid username or password'}, 400
        pass

    def login(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and user.password == password:
            token = generate_token(user.user_id)
            db.session.add(LoginInfo(user.user_id, token))
            db.session.commit()
            return token, user.user_id
        else:
            return None, None
        pass


class Logout(restful.Resource):
    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        # self.post_parse.add_argument('user_id', type=int, required=True, location='values')
        self.post_parse.add_argument('Authorization', type=unicode, required=True, location='headers')

    def post(self):
        token = self.post_parse.parse_args()['Authorization']
        print token
        login_info = LoginInfo.query.filter(LoginInfo.token == token).first()
        if login_info is not None:
            db.session.delete(login_info)
            db.session.commit()
            return {'message': 'logout success'}
        else:
            return {'message': 'token error'}



