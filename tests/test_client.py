#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_client
----------------------------------

Tests for `Client` class.
"""

import unittest
import vcr as vcr_module

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

    def test_valid_session_initialized_silently(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/valid_login.json',
            filter_post_data_parameters=['j_password']
        ):
            client = Client(email=self.email, password=self.password)
            self.assertIsInstance(client, Client)

    def test_me_returns_user_object(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            user = self.get_session().me()
            self.assertIsInstance(user, User)

    def test_client_session_is_cached_and_not_requires_additional_request(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['password'],
            record_mode='once'
        ):
            user = self.get_session()
            user.me()
            user.me()

    def test_user_data_could_be_refreshed_from_the_server(self):
        with self.assertRaises(vcr_module.errors.CannotOverwriteExistingCassetteException):
            with vcr.use_cassette('fixtures/vcr_cassettes/me.json',
                filter_post_data_parameters=['password'],
                record_mode='once'
            ):
                user = self.get_session()
                user.me(refresh=True)
                user.me(refresh=True)

#access-control-max-age": "21600"

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
