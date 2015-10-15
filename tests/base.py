#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from . import test_helper
from anydo_api.client import Client
from anydo_api.user import User

__all__ = ['TestCase']

class TestCase(unittest.TestCase):
    """Test case base class for all tests."""

    def setUp(self, *args, **kwargs):
        super(TestCase, self).setUp(*args, **kwargs)

        credentials = test_helper.credentials_file()
        self.username = credentials['username']
        self.password = credentials['password']
        self.email    = credentials['email']

        with test_helper.vcr.use_cassette(
            'fixtures/vcr_cassettes/valid_login.json',
            filter_post_data_parameters=['j_password']
        ):
            session = Client(email=self.email, password=self.password)
            self.session = session

        with test_helper.vcr.use_cassette(
            'fixtures/vcr_cassettes/me.json',
            filter_post_data_parameters=['j_password']
        ):
            self.me = self.session.me()

    def tearDown(self, *args, **kwargs):
        super(TestCase, self).tearDown(*args, **kwargs)

        del self.username
        del self.password
        del self.email
        del self.session


