#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from flask import Flask, g
import flask_restful as restful
from sqlalchemy import event
from tweetapi.database import db

from tweetapi.resources.Login import Login, Logout
from tweetapi.resources.Registration import Registration
from tweetapi.resources.Tweet import Tweet
from tweetapi.resources.Comment import Comment, CommentTable
from tweetapi.resources.Image import Image

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)


with app.app_context():
    db.create_all()


api = restful.Api(app)
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout', '/logout/<int:user_id>')
api.add_resource(Registration, '/registration')
api.add_resource(Tweet, '/tweet', '/tweet/<int:tweet_id>', '/tweet/user/<int:user_id>')
api.add_resource(Comment, '/comment', '/comment/<int:tweet_id>')
api.add_resource(Image, '/image', '/image/<filename>', endpoint='image')

if __name__ == '__main__':
    app.run(debug=True)






