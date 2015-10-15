#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_client
----------------------------------

Tests for `Client` class.
"""

import unittest

from . import base
from .test_helper import vcr

from anydo_api.client import Client
from anydo_api.user import User
from anydo_api.errors import *


class TestClient(base.TestCase):

    def test_new_client_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_login.json'):
            with self.assertRaises(UnauthorizedError):
                Client(email='***', password='***')

    # split test by x2
    def test_test_me_returns_user_object(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/valid_login.json',
            filter_post_data_parameters=['j_password'],
            record_mode='new_episodes'
        ):
            client = Client(email=self.email, password=self.password)
            user = client.me()
            self.assertIsInstance(user, User)

    def test_client_session_is_cached_and_not_requires_additional_request(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['password']
        ):
            self.session.me()

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
