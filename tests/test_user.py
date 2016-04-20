#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_user
----------------------------------

Tests for `User` class.
"""

import unittest
import json

from tests.base import TestCase
from tests.test_helper import vcr, scrub_string

from anydo_api import errors
from anydo_api.client import Client
from anydo_api.user import User


class TestUser(TestCase):

    def test_user_creation_reraises_occured_errors(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_create_user.json'):
            with self.assertRaises(errors.BadRequestError):
                Client.create_user(name='*', email='*', password='*')

    def test_valid_user_creation_returns_user_intance(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/valid_create_user.json',
            before_record_response=scrub_string(self.password),
            filter_post_data_parameters=['password', 'j_password'],
            record_mode='new_episodes'
        ):
            user = Client.create_user(name=self.username, email=self.email, password=self.password)
            self.assertIsInstance(user, User)

    def test_duplicate_user_creation_raises_conflict(self):
        with vcr.use_cassette('fixtures/vcr_cassettes/duplicate_user.json',
            filter_post_data_parameters=['password']
        ):
            with self.assertRaises(errors.ConflictError):
                Client.create_user(name=self.username, email=self.email, password=self.password)

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
            user = self.get_session().get_user(refresh=True)
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
            user = self.get_session().get_user(refresh=True)
            self.assertEqual(new_name, user.name)

    def test_can_not_set_unmapped_attributes(self):
        user = self.get_me()
        with self.assertRaises(errors.ModelAttributeError):
            user['suppa-duppa'] = 1


    def test_unchanged_data_dont_hit_an_api(self):
        user = self.get_me()
        with vcr.use_cassette(
            'fixtures/vcr_cassettes/fake.json',
            record_mode='none'
        ):
            name = user.name
            user['name'] = name[:]
            user.save()

    def test_new_user_could_be_deleted_instanly(self):
        fake_email = 'unknown@xxx.yyy'
        fake_password = 'fake_password'

        with vcr.use_cassette('fixtures/vcr_cassettes/create_fake_user_to_destroy.json',
            before_record_response=scrub_string(fake_password),
            filter_post_data_parameters=['password', 'j_password']
        ):
            user = Client.create_user(name='fake', email=fake_email, password=fake_password)

        with vcr.use_cassette('fixtures/vcr_cassettes/user_destroy_valid.json',
            before_record_response=scrub_string(fake_password),
            filter_post_data_parameters=['password'],
        ):
            user.destroy()

        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_login_after_destroy.json',
            filter_post_data_parameters=['password', 'j_password'],
        ):
            with self.assertRaises(errors.UnauthorizedError):
                Client(email=fake_email, password=fake_password)

    def test_existent_user_could_be_deleted(self):
        fake_email = 'unknown@xxx.yyy'
        fake_password = 'fake_password'

        with vcr.use_cassette('fixtures/vcr_cassettes/create_fake_user_to_destroy2.json',
            before_record_response=scrub_string(fake_password),
            filter_post_data_parameters=['password', 'j_password']
        ):
            Client.create_user(name='fake', email=fake_email, password=fake_password)

        with vcr.use_cassette('fixtures/vcr_cassettes/fake_user_login.json',
            before_record_response=scrub_string(fake_password),
            filter_post_data_parameters=['j_password'],
            record_mode='new_episodes'
        ):
            user = Client(email=fake_email, password=fake_password).get_user()

        with vcr.use_cassette('fixtures/vcr_cassettes/user_destroy_valid2.json',
            before_record_response=scrub_string(fake_password),
            filter_post_data_parameters=['password'],
        ):
            user.destroy()

        with vcr.use_cassette('fixtures/vcr_cassettes/invalid_login_after_destroy.json',
            filter_post_data_parameters=['password', 'j_password'],
        ):
            with self.assertRaises(errors.UnauthorizedError):
                Client(email=fake_email, password=fake_password)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
