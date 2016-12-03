#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import request
from tweetapi.database import db, User
class Login(restful.Resource):
    def post(self):
        json_data = request.get_json()
        print json_data
        username = json_data['username']
        password = json_data['password']
        token, user_id = self.verifyPassword(username, password)
        if token is not None:
            return {'token':token, 'user_id':user_id}
        else:
            return {'error':'invalid username or password'}
        pass

    def verifyPassword(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and user.password == password:
            return 'aaabbbccc', user.user_id
        else:
            return None, None
        pass