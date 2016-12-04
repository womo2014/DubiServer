#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os, json
from werkzeug.datastructures import Headers
import tweetapi
import unittest


class TweetapiTestCase(unittest.TestCase):
    token = ''

    def setUp(self):
        tweetapi.app.config['TESTING'] = True
        self.app = tweetapi.app.test_client()
        with tweetapi.app.app_context():
            tweetapi.db.create_all()

    def tearDown(self):
        print 'tearDown'
        with tweetapi.app.app_context():
            # tweetapi.db.drop_all()
            for user in tweetapi.database.User.query.all():

                tweetapi.db.session.delete(user)
                print user
                tweetapi.db.session.commit()
            pass

    def get_headers(self):
        headers = Headers()
        headers.add('content-type', 'application/json')
        headers.add('Authorization', 'Token ' + self.token)
        return headers

    def registration(self, username, password):
        data = json.dumps({'username': username, 'password': password})
        rv = self.app.post('/registration', data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def login(self, username, password):
        data = json.dumps({'username': username, 'password': password})
        rv = self.app.post('/login', data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def logout(self, user_id):
        data = json.dumps({'user_id': user_id})
        rv = self.app.post('/logout', data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def post_tweet(self, user_id, description, filename):
        data = self.post_image(user_id, filename)
        assert 'url' in data
        data = json.dumps({
            "user_id": user_id,
            'description': description,
            'image_url': json.loads(data)['url']
        })
        rv = self.app.post('tweet', data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def post_image(self, user_id, filename):
        path = r'D:\DATA\python\AndroidApp\test'
        with open(os.path.join(path,filename), 'rb') as image_file:
            image_data = image_file.read()
        data = json.dumps({
            'user_id': user_id,
            'filename': filename,
            'image': base64.b64encode(image_data)
        })
        rv = self.app.post('/image', data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def get_image(self, user_id, url):
        path = r'D:\DATA\python\AndroidApp\test'
        data = dict(user_id=user_id)
        rv = self.app.get(url, data=data, headers=self.get_headers())
        with open('%r_test.png' % user_id, 'wb') as image_file:
            image_file.write(rv.data)
        return rv

    def test_register(self):
        data = self.registration('womo2', '100')
        assert 'success' in data
        data = self.registration('womo2', '100')
        assert 'duplicate username' in data
        data = self.login('womo2', '100')
        assert 'token' in data


    def test_login_logout(self):
        self.registration('womo1', 'xxx')
        data = self.login('womo1', 'xxx')
        assert 'token' in data
        data = json.loads(data)
        self.token = data['token']
        user_id = data['user_id']
        data = self.post_tweet(user_id, '今天天气不错', 'test1.png')
        assert 'tweet_id' in data
        self.logout(user_id)
        data = self.post_tweet(user_id, '今天天气不错', 'test1.png')
        assert 'Unauthorized access' in data

    def test_post_tweet(self, username='womo'):
        self.registration(username, 'xxx')
        data = self.login(username, 'xxx')
        assert 'token' in data
        data = json.loads(data)
        self.token = data['token']
        user_id = data['user_id']
        data = self.post_tweet(user_id, '今天天气不错', 'test1.png')
        assert 'tweet_id' in data
        return data

    def test_get_image(self):
        data = self.test_post_tweet('womo1')
        data = json.loads(data)
        user_id = data['user']['user_id']
        url = data['image_url']
        rv = self.get_image(user_id, url+'1')
        assert rv.status == '404 NOT FOUND'
        rv = self.get_image(user_id, url)
        assert '200' in rv.status



if __name__ == '__main__':
    unittest.main()