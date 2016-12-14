#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import flask_restful as  restful
import sys
from flask_restful import marshal,marshal_with, reqparse, abort
from tweetapi.resources import comment_fields, auth
from tweetapi.database import db, User, Tweet, Comment as CommentTable


class Comment(restful.Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('content', type=unicode, required=True, location='json',
                                     help='require content')
        self.post_parse.add_argument('from_user_id', type=int, required=True, location='json',
                                     help='require from_user_id')
        self.post_parse.add_argument('to_user_id', type=int, required=False, location='json')

        self.get_parse = reqparse.RequestParser()
        self.get_parse.add_argument('last_id', type=int, required=False, location='args')
        self.get_parse.add_argument('limit', type=int, required=True, location='args')

    def get(self, comment_id = None, tweet_id = None):
        if comment_id is not None:
            # /comment/<int:comment_id>
            comment = CommentTable.query.get(comment_id)
            if comment is None:
                abort(404)
            else:
                return marshal(comment, comment_fields)
        elif tweet_id is not None:
            # /comment/<int:comment_id>
            args = self.get_parse.parse_args()
            last_id = args['last_comment_id'] if args['last_comment_id'] is not None else sys.maxsize
            limit = args['limit']
            tweet_id = args['tweet_id'] if tweet_id is None else tweet_id
            if tweet_id is not None:
                tweet = Tweet.query.get(tweet_id)
                if tweet is None:
                    abort(404)
                else:
                    return {
                        'comments': [marshal(comment, comment_fields) for comment in tweet.comments
                            .filter(CommentTable.comment_id < last_id)
                            .limit(limit)]
                    }
            else:
                abort(400)
        pass

    @marshal_with(comment_fields)
    def post(self, tweet_id):
        args = self.post_parse.parse_args()
        content = args['content']
        from_user_id = args['from_user_id']
        to_user_id = args['to_user_id']

        if tweet_id is None or content is None or from_user_id is None:
            abort(400)
        else:
            comment = CommentTable(tweet_id, content, from_user_id, to_user_id)
            db.session.add(comment)
            db.session.commit()
            return comment
        pass

    def delete(self, tweet_id, comment_id):
        # Todo: Delete comment.

        return {'message': 'delete comment success.'}
        pass
