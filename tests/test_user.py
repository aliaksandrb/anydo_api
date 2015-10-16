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
            user = self.get_me()

            self.assertEqual(self.username, user['name'])
            self.assertEqual(self.email, user['email'])

    def test_user_attributes_accessible_directly(self):
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            user = self.get_me()

            self.assertEqual(self.username, user.name)
            self.assertEqual(self.email, user.email)

    def test_user_could_be_updated_successfully_by_index(self):
        new_name = 'New Name'
        user = self.get_me()

        with vcr.use_cassette(
            'fixtures/vcr_cassettes/user_update_valid.json',
            filter_post_data_parameters=['j_password']
        ):
            user['name'] = new_name
            user.save()
            self.assertEqual(new_name, user['name'])

        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me_updated.json',
        ):
            user = self.get_session().me(refresh=True)
            self.assertEqual(new_name, user['name'])

    def test_user_could_be_updated_successfully_by_attribute(self):
        new_name = 'New Name'
        user = self.get_me()

        with vcr.use_cassette(
            'fixtures/vcr_cassettes/user_update_valid.json',
            filter_post_data_parameters=['j_password']
        ):
            user.name = new_name
            user.save()
            self.assertEqual(new_name, user.name)

        with vcr.use_cassette(
            'fixtures/vcr_cassettes/me_updated.json',
        ):
            user = self.get_session().me(refresh=True)
            self.assertEqual(new_name, user.name)

    def test_can_not_set_unmapped_attributes(self):
        user = self.get_me()
        with self.assertRaises(AttributeError):
            user['suppa-duppa'] = 1


# cachec refresh
# update not changed?
# Server Error tests

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
