#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import request
import sys
from flask_restful import marshal, reqparse, abort
from tweetapi.resources import tweet_fields, auth
from tweetapi.database import db, User, Tweet as TweetTable


class Tweet(restful.Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('user_id', type=int, required=True, help='No user_id', location='json')
        self.post_parse.add_argument('description', type=unicode, required=True, help='No description', location='json')
        self.post_parse.add_argument('image_url', type=unicode, required=False, location='json')

        self.get_parse = reqparse.RequestParser()
        self.get_parse.add_argument('last_tweet_id', type=int, required=False, location='args')
        self.get_parse.add_argument('limit', type=int, required=False, location='args')
        self.get_parse.add_argument('tweet_id', type=int, required=False, location='args')
        self.get_parse.add_argument('user_id', type=int, required=False, location='args')
        pass

    def get(self, tweet_id = None, user_id = None):
        args = self.get_parse.parse_args()
        last_tweet_id = args['last_tweet_id'] if args['last_tweet_id'] is not None else sys.maxsize
        limit = args['limit']
        tweet_id = args['tweet_id'] if tweet_id is None else tweet_id
        user_id = args['user_id'] if user_id is None else user_id
        # /tweet/<tweet_id>
        if tweet_id is not None:
            print tweet_id
            tweet = TweetTable.query.get(tweet_id)
            print tweet
            if tweet is None:
                abort(404)
            return marshal(tweet, tweet_fields)
        # /tweet/user/<user_id>/
        elif user_id is not None:
            print user_id
            user = User.query.get(user_id)
            if user is not None:
                return {'tweets': [marshal(tweet, tweet_fields) for tweet in user.tweets
                    .filter(TweetTable.tweet_id < last_tweet_id)
                    .order_by(TweetTable.tweet_id.desc())
                    .limit(limit)]}
            else:
                abort(404)
        # /tweet
        else:
            return {'tweets': [marshal(tweet, tweet_fields) for tweet in TweetTable.query
                .filter(TweetTable.tweet_id < last_tweet_id)
                .order_by(TweetTable.tweet_id.desc())
                .limit(limit)]}
        pass

    def post(self):
        args = self.post_parse.parse_args()
        print args
        tweet = TweetTable(args['user_id'], args['description'])
        db.session.add(tweet)
        db.session.commit()
        user = User.query.get(args['user_id'])
        print user
        return marshal(tweet, tweet_fields)
        pass



# tweets = [
#     {
#         'user': {
#             'username': 'womo',
#             'uid': 1,
#             'photo_url': 'http://photo.com'
#         },
#         'description': 'today is so nice!',
#         'stared': True,
#         'tweet_id': 1,
#         'image_url': 'http://image.com'
#     }
# ]