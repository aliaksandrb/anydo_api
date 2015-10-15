#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_user
----------------------------------

Tests for `User` class.
"""

import unittest
import vcr
import json


from anydo_api.errors import *
from anydo_api import client
from anydo_api import user

vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='tests',
)

__credentials_file = 'test_credentials.json'

try:
    with open(__credentials_file) as f:
        credentials = json.load(f)
except FileNotFoundError as e:
    error = FileNotFoundError('{} file is required for remote API testing'
        .format(__credentials_file))
    error.__cause__ = e
    raise error
except ValueError as e:
    error = ValueError('{} file is bad formatted'.format(__credentials_file))
    error.__cause__ = e
    raise error


if len([item for item in credentials.items() if item[0] in ('username', 'password', 'email')
                                                and item[1] != '']) < 3:
    raise ValueError('{} file has missed required keys or values'.format(__credentials_file))

class TestUser(unittest.TestCase):

    def setUp(self):
        try:
            self.User = user.User
        except AttributeError: pass

        self.username = credentials['username']
        self.password = credentials['password']
        self.email = credentials['email']

    def tearDown(self):
        if hasattr(self, 'User'): del self.User
        del self.username
        del self.password
        del self.email


    def test_implemented(self):
        self.assertTrue(hasattr(user, 'User'))

    def test_user_creation_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_create_user.json'):
            with self.assertRaises(BadRequestError):
                self.User.create(name='*', email='*', password='*')

    def test_valid_user_creation_returns_user_intance(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/valid_create_user.json',
            before_record_response=scrub_string(self.password),
            filter_post_data_parameters=['password']
        ):
            user = self.User.create(name=self.username, email=self.email, password=self.password)
            self.assertIsInstance(user, self.User)

    def test_duplicate_user_creation_raises_conflict(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/duplicate_user.json',
            filter_post_data_parameters=['password']
        ):
            with self.assertRaises(ConflictError):
                self.User.create(name=self.username, email=self.email, password=self.password)

# Server Error tests
# check attributes of new user

def scrub_string(string, replacement='******'):
    def before_record_response(response):
        text = response['body']['string'].decode('utf-8')
        text.replace(string, replacement)
        text_dict = json.loads(text)
        text_dict['auth_token'] = replacement
        response['body']['string'] = json.dumps(text_dict).encode('utf-8')

        return response
    return before_record_response


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
