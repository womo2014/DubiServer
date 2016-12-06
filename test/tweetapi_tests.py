#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import os, json
from werkzeug.datastructures import Headers
import tweetapi
import unittest


class TweetapiTestCase(unittest.TestCase):
    token = ''
    user_id = 0
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
            'description': description,
            'image_url': json.loads(data)['url']
        })
        rv = self.app.post('/users/%r/tweet' % user_id, data=data, headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def delete_tweet(self, user_id, tweet_id):
        rv = self.app.delete('/users/%r/tweet/%r' % (user_id, tweet_id), headers=self.get_headers())
        print rv.data, rv.status
        return rv.data

    def post_comment(self, tweet_id):
        data = json.dumps({
            'content': 'nice',
            'from_user_id': unicode(self.user_id),
        })
        rv = self.app.post('/tweet/%r/comment' % tweet_id, data=data, headers=self.get_headers())
        print rv.status, rv.data
        return rv.data

    def delete_comment(self, tweet_id, comment_id):
        rv = self.app.delete('/tweet/%r/comment/%r' % (tweet_id, comment_id), headers=self.get_headers())
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
        self.user_id = data['user_id']
        data = self.post_tweet(self.user_id, '今天天气不错', 'test1.png')
        assert 'tweet_id' in data
        self.logout(self.user_id)
        data = self.post_tweet(self.user_id, '今天天气不错', 'test1.png')
        assert 'Unauthorized access' in data

    def test_post_tweet(self, username='womo'):
        self.registration(username, 'xxx')
        data = self.login(username, 'xxx')
        assert 'token' in data
        data = json.loads(data)
        self.token = data['token']
        self.user_id = data['user_id']
        data = self.post_tweet( self.user_id, '今天天气不错', 'test1.png')
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

    def test_post_comment(self):
        data = self.test_post_tweet('womox')
        tweet_id = json.loads(data)['tweet_id']
        data = self.post_comment(tweet_id)
        assert 'comment_id' in data
        return data

    def test_delete_tweet(self):
        data = self.test_post_comment()
        data = json.loads(data)
        tweet_id = data['tweet_id']
        comment_id = data['comment_id']
        data = self.delete_tweet(self.user_id, tweet_id)
        assert 'success' in data
        data = self.delete_tweet(self.user_id, tweet_id)
        assert 'not found' in data
        # Todo: verify the tweet and its comments are all be deleted
        data = self.test_post_comment()
        data = json.loads(data)
        tweet_id = data['tweet_id']
        comment_id = data['comment_id']
        self.registration('womo', 'womo')
        data = self.login('womo', 'womo')
        data = json.loads(data)
        user_id = data['user_id']
        self.token = data['token']
        data = self.delete_tweet(self.user_id, tweet_id)
        assert 'no permission' in data

    def test_delete_comment(self):
        data = self.test_post_comment()
        data = json.loads(data)
        tweet_id = data['tweet_id']
        comment_id = data['comment_id']
        data = self.delete_comment(tweet_id, comment_id)
        assert 'success' in data
        data = self.delete_comment(tweet_id, comment_id)
        # assert 'not found' in data
        pass

    def test_get_tweet(self):
        data = self.test_post_tweet()
        data = json.loads(data)
        tweet_id = data['tweet_id']
        user_id = data['user']['user_id']

if __name__ == '__main__':
    unittest.main()