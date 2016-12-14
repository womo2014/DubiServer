#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import g, request
import sys
from flask_restful import marshal, reqparse, abort, marshal_with
from tweetapi.resources import tweet_fields, auth, user_info_fields
from tweetapi.database import db, User, Tweet as TweetTable

class UserApi(restful.Resource):
    decorators = [auth.login_required]

    def __init__(self):
        pass

    @marshal_with(user_info_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            return {'message', 'user no found'}, 404
        if user in g.user.friends:
            user.is_friend = True
        if user in g.user.fans:
            user.is_fan = True
        return user

    def put(self, user_id):
        if g.user.user_id != user_id:
            return {'message', 'no permission'}, 401
        pass

