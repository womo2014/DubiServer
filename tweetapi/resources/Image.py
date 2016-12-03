#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os
from flask import Flask, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from tweetapi import config
from flask import request
import flask_restful as  restful
import sys
from flask_restful import marshal, reqparse, abort
from tweetapi.resources import tweet_fields, auth
from tweetapi.database import db, User, Tweet as TweetTable


class Image(restful.Resource):
    # decorators = [auth.login_required]

    def __init__(self):
        self.get_parse = reqparse.RequestParser()
        self.get_parse.add_argument('filename', location='args')

        self.post_parse = reqparse.RequestParser()
        self.post_parse.add_argument('filename', required=True, location='json')
        self.post_parse.add_argument('image', required=True, location='json')

    def get(self, filename = None):
        args = self.get_parse.parse_args()
        filename = args['filename'] if filename is None else filename
        return send_file(os.path.join(config.UPLOAD_FOLDER, filename))

    def post(self):
        args = self.post_parse.parse_args()
        filename = args['filename']
        if allowed_file(filename):
            filename = secure_filename(filename)
            print filename
            image_data = base64.b64decode(args['image'])
            with open(os.path.join(config.UPLOAD_FOLDER, filename), 'wb') as image:
                image.write(image_data)
            return {'url':url_for('image', filename=filename)}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS
