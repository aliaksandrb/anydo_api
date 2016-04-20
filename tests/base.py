#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from tests import test_helper
from anydo_api.client import Client

__all__ = ('TestCase')

class TestCase(unittest.TestCase):
    """Test case base class for all tests."""

    def setUp(self, *args, **kwargs):
        """Load from environment valid AnyDo credentials required for authentication."""
        super(TestCase, self).setUp(*args, **kwargs)

        credentials = test_helper.credentials_values()
        self.username = credentials['username']
        self.password = credentials['password']
        self.email    = credentials['email']

    def tearDown(self, *args, **kwargs):
        super(TestCase, self).tearDown(*args, **kwargs)

        del self.username
        del self.password
        del self.email

    def get_session(self):
        """
        Returns a cached authenticated session.
        """
        with test_helper.vcr.use_cassette(
            'fixtures/vcr_cassettes/valid_login.json',
            filter_post_data_parameters=['j_password']
        ):
            session = Client(email=self.email, password=self.password)
        return session

    def get_me(self):
        """
        Returns a authenticated user object.
        """
        with test_helper.vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            return self.get_session().get_user()

