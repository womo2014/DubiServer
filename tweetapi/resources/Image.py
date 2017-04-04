#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os

import time
from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from tweetapi import config
from flask import request
import flask_restful as  restful
import sys
from flask_restful import marshal, reqparse, abort
from werkzeug.datastructures import FileStorage
from tweetapi.resources import tweet_fields, auth
from tweetapi.database import db, User, Tweet as TweetTable


class Image(restful.Resource):

    def __init__(self):
        self.get_parse = reqparse.RequestParser()
        self.get_parse.add_argument('filename', location='args')
        self.get_parse.add_argument('user_id', location='args')

        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('user_id', type=int, required=True,
                                     location='form', help='need user_id')
        self.post_parse.add_argument('image', type=FileStorage,  required=True,
                                     location='files', help='need iamge file')

    def get(self, filename = None):
        args = self.get_parse.parse_args()
        filename = args['filename'] if filename is None else filename
        path = os.path.join(config.UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            return send_file(path, cache_timeout=3600*24*100)
        else:
            abort(404)

    @auth.login_required
    def post(self):
        args = self.post_parse.parse_args()
        image = args['image']
        user_id = args['user_id']
        if image and allowed_file(image.filename):
            filename = base64.b64encode('%r_%r' % (user_id, time.time()))[:-2]+'.'+image.filename.rsplit('.', 1)[1]
            print filename
            image.save(os.path.join(config.UPLOAD_FOLDER, filename))
            return {'url': url_for('image', filename=filename)}
        else:
            abort(400)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS
