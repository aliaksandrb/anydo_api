#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
anydo_api.client.

`Client` class.
"""

import requests

from anydo_api import request
from anydo_api.constants import CONSTANTS
from anydo_api.user import User

__all__ = ('Client')

class Client(object):
    """
    `Client` is the interface for communication with an API.

    Responsible for authentication and session management.
    """

    def __init__(self, email, password):
        """Constructor for Client."""
        self.session = self.__log_in(email, password)
        self.password = password
        self.user = None

    def get_user(self, refresh=False):
        """Return a user object currently logged in."""
        if not self.user or refresh:
            data = request.get(
                url=CONSTANTS.get('ME_URL'),
                session=self.session
            )

            data.update({'password': self.password})
            self.password = None
            self.user = User(data_dict=data, session=self.session)

        return self.user

    def __log_in(self, email, password):
        """
        Authentication base on `email` and `password`.

        Return an actual session, used internally for all following requests to API.
        """
        credentials = {
            'j_username': email,
            'j_password': password,
            '_spring_security_remember_me': 'on'
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.session = requests.Session()

        request.post(
            url=CONSTANTS.get('LOGIN_URL'),
            session=self.session,
            headers=headers,
            data=credentials,
            response_json=False
        )

        return self.session

    @classmethod
    def create_user(cls, **fields):
        """Create new user by required parameters."""
        User.check_for_missed_fields(fields)

        json_data = {
            'name': fields.get('name'),
            'username': fields.get('email'),
            'password': fields.get('password'),
            'emails': fields.get('emails', fields.get('email')),
            'phoneNumbers': fields.get('phone_numbers', [])
        }

        request.post(
            url=CONSTANTS.get('USER_URL'),
            json=json_data
        )

        user = Client(email=fields.get('email'), password=fields.get('password')).get_user()
        return user
