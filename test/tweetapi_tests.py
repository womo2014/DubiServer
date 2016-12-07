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

    def post_tweet(self, user_id, description, filename=None):
        if filename is not None:
            data = self.post_image(user_id, filename)
            assert 'url' in data
            url = json.loads(data)['url']
        else:
            url = None
        data = json.dumps({
            'description': description,
            'image_url': url
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
        data = {
            'image': open(os.path.join(path,filename), 'rb'),
            'user_id': user_id
        }
        rv = self.app.post('/image',
                           content_type='multipart/form-data',
                           data=data,
                           headers=self.get_headers())
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
        data = self.post_tweet(self.user_id, '今天天气不错')
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
        data = self.test_post_tweet('aaa')
        data = self.test_post_tweet('bbb')
        data = self.test_post_tweet('ccc')
        data = self.test_post_tweet('ccc')
        data = json.loads(data)
        tweet_id = data['tweet_id']
        user_id = data['user']['user_id']
        self.registration('1womo', 'xxx')
        data = json.loads(self.login('1womo', 'xxx'))
        self.token = data['token']
        self.user_id = data['user_id']
        rv = self.app.post('/users/%r/friends' % self.user_id,
                           data=json.dumps({'follow_user_id': unicode(user_id)}),
                           headers=self.get_headers())
        print rv.data, rv.status
        rv = self.app.get('/users/%r/friends/tweet?limit=10' % self.user_id,
                          headers=self.get_headers())
        print rv.data, rv.status
        rv = self.app.get('/tweet?limit=3',
                          headers=self.get_headers())
        print rv.data, rv.status

    def test_follow_user(self):
        user_id = []
        token = []
        self.registration('womo', 'xxx')
        data = json.loads(self.login('womo', 'xxx'))
        token.append(data['token'])
        user_id.append(data['user_id'])
        self.registration('womo1', 'xxx')
        data = json.loads(self.login('womo1', 'xxx'))
        token.append(data['token'])
        user_id.append(data['user_id'])
        self.token = token[0]
        rv = self.app.post('/users/%r/friends' % user_id[0],
                           data=json.dumps({'follow_user_id':unicode(user_id[1])}),
                           headers=self.get_headers())
        print rv.data, rv.status
        rv = self.app.get('/users/%r/friends' % user_id[0],
                          headers=self.get_headers())
        print rv.data, rv.status
        rv = self.app.get('/users/%r/fans' % user_id[1],
                          headers=self.get_headers())
        print rv.data, rv.status
        rv = self.app.delete('/users/%r/friends/%r' % (user_id[0], user_id[1]),
                           headers=self.get_headers())
        print rv.data, rv.status


if __name__ == '__main__':
    unittest.main()