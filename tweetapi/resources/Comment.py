#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import flask_restful as restful
from flask import g
import sys, json
from flask_restful import marshal,marshal_with, reqparse, abort
from tweetapi.resources import comment_fields, auth, tweet_fields
from tweetapi.database import db, User, Tweet, Comment as CommentTable, Notification
from tweetapi.xmpush import sender, PushMessage, Constants
from tweetapi.config import PACKAGE_NAME

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

    def get(self, comment_id=None, tweet_id=None):
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
            last_id = sys.maxsize if args['last_id'] == -1 else args['last_id']
            limit = args['limit']
            tweet_id = args['tweet_id'] if tweet_id is None else tweet_id
            if tweet_id is not None:
                tweet = Tweet.query.get(tweet_id)
                if tweet is None:
                    abort(404)
                else:
                    return [marshal(comment, comment_fields) for comment in
                            tweet.comments.filter(CommentTable.comment_id > last_id).limit(limit)]
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
        tweet = Tweet.query.get(tweet_id)
        if tweet is None or from_user_id != g.user.user_id:
            abort(400)
        if to_user_id is not None and User.query.get(to_user_id) is None:
            abort(400)
        comment = CommentTable(tweet_id, content, from_user_id, to_user_id)
        content = u'评论: %s' % comment.content
        if to_user_id is not None:
            content = u'回复 %s: %s' % (User.query.get(to_user_id).username, comment.content)
        db.session.add(comment)
        db.session.commit()
        db.session.add(Notification(tweet.user_id, comment.comment_id))
        message = PushMessage() \
            .restricted_package_name(PACKAGE_NAME) \
            .title(g.user.username).description(content) \
            .pass_through(0).payload(u'payloadddddd') \
            .notify_type(1) \
            .extra({Constants.extra_param_notify_effect: Constants.notify_activity,
                    Constants.extra_param_intent_uri:
                        'intent:#Intent;component=cc.wo_mo.dubi/.ui.CommentActivity;S.tweet=%s;end' % json.dumps(marshal(tweet, tweet_fields))})
        if tweet.user_id != from_user_id:
            sender.send_to_user_account(message.message_dict(), unicode(tweet.user_id))
        if to_user_id is not None:
            db.session.add(Notification(to_user_id, comment.comment_id))
            if to_user_id != from_user_id:
                sender.send_to_user_account(message.message_dict(), unicode(to_user_id))
        db.session.commit()
        return comment
        pass

    def delete(self, tweet_id, comment_id):
        comment = CommentTable.query.get(comment_id)
        tweet = Tweet.query.get(tweet_id)
        if comment in tweet.comments:
            if tweet.user_id == g.user.user_id or comment.from_user_id == g.user.user_id:
                db.session.delete(comment)
                db.session.commit()
                return {'message': 'delete comment success.'}
            else:
                return {'error': 'you have no permission'}, 400
        else:
            return {'error': 'bad request'}, 400
        pass
