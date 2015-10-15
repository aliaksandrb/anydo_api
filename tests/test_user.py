#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_user
----------------------------------

Tests for `User` class.
"""

import unittest
import json

from .base import TestCase
from .test_helper import vcr, scrub_string

from anydo_api.client import Client
from anydo_api.user import User
from anydo_api.errors import *


class TestUser(TestCase):

    def test_user_creation_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_create_user.json'):
            with self.assertRaises(BadRequestError):
                User.create(name='*', email='*', password='*')

    def test_valid_user_creation_returns_user_intance(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/valid_create_user.json',
            before_record_response=scrub_string(self.password),
            filter_post_data_parameters=['password']
        ):
            user = User.create(name=self.username, email=self.email, password=self.password)
            self.assertIsInstance(user, User)

    def test_duplicate_user_creation_raises_conflict(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/duplicate_user.json',
            filter_post_data_parameters=['password']
        ):
            with self.assertRaises(ConflictError):
                User.create(name=self.username, email=self.email, password=self.password)

    def test_user_has_appropriate_attributes(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            user = self.session.me()

            self.assertEqual(self.username, user['name'])
            self.assertEqual(self.email, user['email'])

    def test_user_attributes_accessible_directly(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            user = self.session.me()

            self.assertEqual(self.username, user.name)
            self.assertEqual(self.email, user.email)

# aliases name/username?
# change attrs and save
# Server Error tests

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
