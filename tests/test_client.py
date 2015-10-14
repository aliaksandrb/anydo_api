#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_client
----------------------------------

Tests for `client` module.
"""

import unittest
import vcr
import json
import requests

from anydo_api import client

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

class TestClient(unittest.TestCase):

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

    def test_class_exists(self):
        self.assertTrue(hasattr(client, 'Client'))

    def test_knows_about_constants(self):
        self.assertTrue(hasattr(client, 'SERVER_API_URL'))
        self.assertTrue(hasattr(client, 'CONSTANTS'))

        self.assertTrue(client.CONSTANTS.get('SERVER_API_URL'))
        self.assertTrue(client.CONSTANTS.get('LOGIN_URL'))
        self.assertTrue(client.CONSTANTS.get('ME_URL'))


    def test_new_client_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_login.json'):
            with self.assertRaises(client.Unauthorized):
                self.client(email='***', password='***')

    def test_test_me_returns_user_object_json(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/valid_login.json',
            filter_post_data_parameters=['j_password'],
            record_mode='new_episodes'
        ):
            client = self.client(email=self.email, password=self.password)
            user = client.me()
            self.assertEqual(self.email, user['email'])
            self.assertEqual(self.username, user['name'])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
