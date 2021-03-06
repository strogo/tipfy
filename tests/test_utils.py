# -*- coding: utf-8 -*-
"""
    Tests for tipfy utils
"""
import unittest
from nose.tools import raises

import werkzeug

from tipfy import (RequestHandler, Response, Rule, Tipfy, redirect,
    redirect_to, render_json_response)


class HomeHandler(RequestHandler):
    def get(self, **kwargs):
        return 'Hello, World!'


class ProfileHandler(RequestHandler):
    def get(self, **kwargs):
        return 'Username: %s' % kwargs.get('username')


class RedirectToHandler(RequestHandler):
    def get(self, **kwargs):
        username = kwargs.get('username', None)
        if username:
            return redirect_to('profile', username=username)
        else:
            return redirect_to('home')


class RedirectTo301Handler(RequestHandler):
    def get(self, **kwargs):
        username = kwargs.get('username', None)
        if username:
            return redirect_to('profile', username=username, _code=301)
        else:
            return redirect_to('home', _code=301)


class RedirectToInvalidCodeHandler(RequestHandler):
    def get(self, **kwargs):
        return redirect_to('home', _code=405)


def get_app():
    return Tipfy(rules=[
        Rule('/', endpoint='home', handler=HomeHandler),
        Rule('/people/<string:username>', endpoint='profile', handler=ProfileHandler),
        Rule('/redirect_to/', endpoint='redirect_to', handler=RedirectToHandler),
        Rule('/redirect_to/<string:username>', endpoint='redirect_to', handler=RedirectToHandler),
        Rule('/redirect_to_301/', endpoint='redirect_to', handler=RedirectTo301Handler),
        Rule('/redirect_to_301/<string:username>', endpoint='redirect_to', handler=RedirectTo301Handler),
        Rule('/redirect_to_invalid', endpoint='redirect_to_invalid', handler=RedirectToInvalidCodeHandler),
    ])


class TestUtils(unittest.TestCase):
    def tearDown(self):
        Tipfy.app = Tipfy.request = None

    #===========================================================================
    # redirect()
    #===========================================================================
    def test_redirect(self):
        response = redirect('http://www.google.com/')

        assert response.headers['location'] == 'http://www.google.com/'
        assert response.status_code == 302

    def test_redirect_301(self):
        response = redirect('http://www.google.com/', 301)

        assert response.headers['location'] == 'http://www.google.com/'
        assert response.status_code == 301

    def test_redirect_no_response(self):
        response = redirect('http://www.google.com/')

        assert isinstance(response, werkzeug.BaseResponse)
        assert response.headers['location'] == 'http://www.google.com/'
        assert response.status_code == 302

    def test_redirect_no_response_301(self):
        response = redirect('http://www.google.com/', 301)

        assert isinstance(response, werkzeug.BaseResponse)
        assert response.headers['location'] == 'http://www.google.com/'
        assert response.status_code == 301

    @raises(AssertionError)
    def test_redirect_invalid_code(self):
        redirect('http://www.google.com/', 404)

    #===========================================================================
    # redirect_to()
    #===========================================================================
    def test_redirect_to(self):
        app = get_app()
        client = app.get_test_client()

        response = client.get('/redirect_to/', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/'
        assert response.status_code == 302


    def test_redirect_to2(self):
        app = get_app()
        client = app.get_test_client()

        response = client.get('/redirect_to/calvin', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/calvin'
        assert response.status_code == 302

        response = client.get('/redirect_to/hobbes', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/hobbes'
        assert response.status_code == 302

        response = client.get('/redirect_to/moe', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/moe'
        assert response.status_code == 302

    def test_redirect_to_301(self):
        app = get_app()
        client = app.get_test_client()

        response = client.get('/redirect_to_301/calvin', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/calvin'
        assert response.status_code == 301

        response = client.get('/redirect_to_301/hobbes', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/hobbes'
        assert response.status_code == 301

        response = client.get('/redirect_to_301/moe', base_url='http://foo.com')
        assert response.headers['location'] == 'http://foo.com/people/moe'
        assert response.status_code == 301

    def test_redirect_to_invalid_code(self):
        app = get_app()
        client = app.get_test_client()

        response = client.get('/redirect_to_invalid', base_url='http://foo.com')
        assert response.status_code == 500

    #===========================================================================
    # render_json_response()
    #===========================================================================
    def test_render_json_response(self):
        response = render_json_response({'foo': 'bar'})

        assert isinstance(response, Response)
        assert response.mimetype == 'application/json'
        assert response.data == '{"foo": "bar"}'
