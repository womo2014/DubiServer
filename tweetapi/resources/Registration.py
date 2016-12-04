#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import request
from tweetapi.database import db, User
class Registration(restful.Resource):
    def post(self):
        json_data = request.get_json()
        username = json_data['username']
        password = json_data['password']
        return self.register(username, password)


    def register(self, username, password):
        if User.query.filter_by(username=username).first() is None:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            return {'message': 'register success'}
        else:
            return {'error': 'duplicate username'}, 400