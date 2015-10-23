#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_constants
----------------------------------

Tests for `Constants` module.
Checks if all the required constants are set in one place
"""

import unittest

import anydo_api.constants as constants

class TestConstants(unittest.TestCase):
    def setUp(self):
        self.consts = constants

    def tearDown(self):
        del self.consts

    def test_all_constants_defined(self):
        self.assertTrue(hasattr(self.consts, 'SERVER_API_URL'))
        self.assertTrue(hasattr(self.consts, 'CONSTANTS'))
        self.assertTrue(hasattr(self.consts, 'TASK_STATUSES'))

        c_dict = self.consts.CONSTANTS
        self.assertTrue(c_dict.get('SERVER_API_URL'))
        self.assertTrue(c_dict.get('LOGIN_URL'))
        self.assertTrue(c_dict.get('ME_URL'))
        self.assertTrue(c_dict.get('USER_URL'))
        self.assertTrue(c_dict.get('TASKS_URL'))
        self.assertTrue(c_dict.get('CATEGORIES_URL'))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
