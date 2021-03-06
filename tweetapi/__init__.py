#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from flask import Flask, g
import flask_restful as restful
from tweetapi.database import db
from tweetapi.resources.Login import Login, Logout
from tweetapi.resources.Registration import Registration
from tweetapi.resources.Tweet import Tweet
from tweetapi.resources.Comment import Comment, CommentTable
from tweetapi.resources.Image import Image
from tweetapi.resources.RelationshipAPI import RelationshipAPI
from tweetapi.resources.UserApi import UserApi
app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)


with app.app_context():
    db.create_all()


api = restful.Api(app)
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Registration, '/registration')
api.add_resource(UserApi,
                 '/users/<int:user_id>')
api.add_resource(Tweet,
                 '/users/<int:user_id>/tweet', # POST, GET
                 '/users/<int:user_id>/tweet/<int:tweet_id>', # DELETE
                 '/users/<int:user_id>/friends/tweet', # GET
                 '/tweet/<int:tweet_id>', # GET
                 '/tweet') # GET
api.add_resource(Comment,
                 '/tweet/<int:tweet_id>/comment', # POST, GET
                 '/tweet/<int:tweet_id>/comment/<int:comment_id>', # DELETE
                 '/comment/<int:comment_id>',) # GET
api.add_resource(RelationshipAPI,
                 '/users/<int:user_id>/friends', # GET POST
                 '/users/<int:user_id>/friends/<int:remove_user_id>', # DELETE
                 '/users/<int:user_id>/fans' # GET
                 )
api.add_resource(Image, '/image', '/image/<filename>', endpoint='image')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')






