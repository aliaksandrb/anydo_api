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

    def tearDown(self):
        if hasattr(self, 'User'): del self.User

    def test_implemented(self):
        self.assertTrue(hasattr(user, 'User'))

    def test_user_creation_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_create_user.json'):
            with self.assertRaises(client.BadRequest):
                self.User.create(name='*', username='*', password='*', emails=[])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
