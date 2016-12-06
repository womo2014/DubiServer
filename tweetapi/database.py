#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import backref

db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(50))
    tweets = db.relationship('Tweet', backref='user', lazy='dynamic', cascade="delete")
    def __init__(self, username, password, photo_url = None):
        self.username = username
        self.password = password
        self.photo_url = photo_url
        pass

    def __repr__(self):
        return '<User id:%r username:%r password:%r photo:%r>' % \
               (self.user_id, self.username, self.password, self.photo_url)

    def get_dict(self):

        pass


class Tweet(db.Model):
    tweet_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.TEXT, nullable=False)
    stared = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    comments = db.relationship('Comment', lazy='dynamic', cascade="delete")

    def __init__(self, user_id, description, image_url=None, stared=False):
        self.description = description
        self.user_id = user_id
        self.image_url = image_url
        self.stared = stared
        pass

    def __repr__(self):
        return '<Tweet id:%r user_id:%r description:%r image_url:%r starred:%r>' % \
               (self.tweet_id, self.user_id, self.description, self.image_url, self.stared)
    pass


class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.TEXT, nullable=False)
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.tweet_id', ondelete='CASCADE'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    # user = db.relationship('User', backref='comments', foreign_keys=from_user_id)

    def __init__(self, tweet_id, content, from_user_id, to_user_id=None):

        self.tweet_id = tweet_id
        self.content = content
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        pass

    def __repr__(self):
        return '<Interaction, id:%r, tweet:%r, content:%r, from:%r, to:%r>' % \
               (self.comment_id, self.tweet_id, self.content, self.from_user_id, self.to_user_id)
        pass

    pass





