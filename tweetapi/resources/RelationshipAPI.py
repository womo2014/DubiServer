#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import g, request
import sys
from flask_restful import marshal, reqparse, abort
from tweetapi.resources import tweet_fields, auth, user_fields
from tweetapi.database import db, User, Tweet as TweetTable


class RelationshipAPI(restful.Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('follow_user_id', type=int, required=True, help='need user_id you follow')
        # self.get_parse = reqparse.RequestParser()
        # self.post_parse.add_argument('last_id', type=int, required=False, location='args')
        # self.post_parse.add_argument('limit', type=int, required=False, location='args')

    def get(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            abort(404)
        else:
            if 'friends' in request.url:
                return {'friends': [marshal(friend, user_fields) for friend in user.friends]}
            elif 'fans' in request.url:
                return {'fans': [marshal(fan, user_fields) for fan in user.fans]}
        pass

    def post(self, user_id):
        if user_id is None or user_id != g.user.user_id:
            abort(400)
        else:
            follow_user_id = self.post_parse.parse_args()['follow_user_id']
            follow_user = User.query.get(follow_user_id)
            if follow_user is None:
                return {'message': 'no such user'}, 400
            elif follow_user in g.user.friends:
                return {'message': 'you have followed this user'}, 400
            else:
                g.user.friends.append(follow_user)
                db.session.commit()
                print g.user.user_id, 'here', [x for x in g.user.friends]
                return {'message': 'follow success'}
        pass

    def delete(self, user_id, remove_user_id):
        if user_id is None or remove_user_id is None or user_id != g.user.user_id:
            abort(400)
        else:
            print g.user.user_id, 'here', [x for x in g.user.friends]
            removed_user = User.query.get(remove_user_id)
            if removed_user is None:
                return {'message': 'no such user'}, 404
            elif removed_user not in g.user.friends:
                return {'message': 'you have not followed this user'}, 404
            else:
                g.user.friends.remove(removed_user)
                db.session.commit()
                return {'message': 'Unfollow success'}
        pass