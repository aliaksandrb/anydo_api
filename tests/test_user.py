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
import requests

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
            self.client = client.Client
        except AttributeError: pass

        self.username = credentials['username']
        self.password = credentials['password']
        self.email = credentials['email']

    def tearDown(self):
        if hasattr(self, 'client'): del self.client
        del self.username
        del self.password
        del self.email

    def test_implemented(self):
        self.assertTrue(hasattr(user, 'User'))


#    def test_new_client_reraises_occured_errors(self):
#        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_login.json'):
#            with self.assertRaises(client.Unauthorized):
#                self.client(email='***', password='***')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
