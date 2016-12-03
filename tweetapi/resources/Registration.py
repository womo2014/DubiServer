#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import request
from tweetapi.database import db, User
class Registration(restful.Resource):
    def post(self):
        json_data = request.get_json()
        print json_data
        username = json_data['username']
        password = json_data['password']
        token, uid = self.register(username, password)
        if token is not None:
            return {'token':token, 'user_id':uid}
        else:
            return {'error':'duplicate username'}
        pass


    def register(self, username, password):
        # db operation

        if User.query.filter_by(username=username).first() is None:
            print username
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            print user
            return 'bbbcccddd', user.user_id
        else:
            return None, None
        pass