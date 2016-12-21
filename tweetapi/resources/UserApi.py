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
        self.post_paarse = reqparse.RequestParser()
        self.post_paarse.add_argument("introduction", type=unicode, location='json')
        self.post_paarse.add_argument("region", type=unicode, location='json')
        self.post_paarse.add_argument("birth", type=unicode, location='json')
        self.post_paarse.add_argument("photo_url", type=unicode, location='json')
        self.post_paarse.add_argument("gender", type=unicode, location='json')
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

    @marshal_with(user_info_fields)
    def post(self, user_id):
        if g.user.user_id != user_id:
            return {'message', 'no permission'}, 401
        data = self.post_paarse.parse_args()
        if data['introduction'] is not None:
            g.user.introduction = data['introduction']
        if data['region'] is not None:
            g.user.region = data['region']
        if data['birth'] is not None:
            g.user.birth = data['birth']
        if data['photo_url'] is not None:
            g.user.photo_url = data['photo_url']
        if data['gender'] is not None:
            g.user.gender = data['gender']
        db.session.commit()
        return g.user
        pass

