#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import flask_restful as  restful
from flask import g, request
import sys
from flask_restful import marshal, reqparse, abort
from tweetapi.resources import tweet_fields, auth
from tweetapi.database import db, User, Tweet as TweetTable


class Tweet(restful.Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('description', type=unicode, required=True,
                                     help='No description', location='json')
        self.post_parse.add_argument('image_url', type=unicode, required=False, location='json')

        self.get_parse = reqparse.RequestParser()
        self.get_parse.add_argument('last_id', type=int, required=False, location='args')
        self.get_parse.add_argument('limit', type=int, required=True,
                                    help='need argument limit like ?limit=10', location='args')
        pass

    def get(self, tweet_id = None, user_id = None):
        args = self.get_parse.parse_args()
        last_id = args['last_id'] if args['last_id'] is not None else sys.maxsize
        limit = args['limit']
        # /tweet/<tweet_id>
        if tweet_id is not None:
            tweet = TweetTable.query.get(tweet_id)
            if tweet is None:
                abort(404)
            return marshal(tweet, tweet_fields)
        elif user_id is not None:
            user = User.query.get(user_id)
            if user is not None:
                # /users/<int:user_id>/friends/tweet
                if 'friends' in request.url:
                    if g.user.user_id != user_id:
                        abort(400)
                    else:
                        tweets = TweetTable.query\
                            .filter(TweetTable.user_id.in_([friend.user_id for friend in user.friends]))\
                            .order_by(TweetTable.tweet_id.desc())\
                            .limit(limit)

                        return {'tweets': [marshal(tweet, tweet_fields) for tweet in tweets]}
                # /users/<int:user_id>/tweet
                else:
                    return {'tweets': [marshal(tweet, tweet_fields) for tweet in user.tweets
                        .filter(TweetTable.tweet_id < last_id)
                        .order_by(TweetTable.tweet_id.desc())
                        .limit(limit)]}
            else:
                abort(404)
        # /tweet
        else:
            return {'tweets': [marshal(tweet, tweet_fields) for tweet in TweetTable.query
                .filter(TweetTable.tweet_id < last_id)
                .order_by(TweetTable.tweet_id.desc())
                .limit(limit)]}
        pass

    def post(self, user_id):
        # /users/<int:user_id>/tweet
        print 'post tweet here'
        if g.user.user_id != user_id:
            abort(400)
        args = self.post_parse.parse_args()
        tweet = TweetTable(user_id, args['description'], args['image_url'])
        db.session.add(tweet)
        db.session.commit()
        return marshal(tweet, tweet_fields)
        pass

    def delete(self, user_id, tweet_id):
        # /users/<int:user_id>/tweet/<int:tweet_id>
        if g.user.user_id != user_id:
            return {'error': 'you have no permission'}, 400
        tweet = TweetTable.query.get(tweet_id)
        if tweet is None or tweet.user.user_id != user_id:
            abort(404)
        else:
            db.session.delete(tweet)
            db.session.commit()
            return {'message': 'delete success'}


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