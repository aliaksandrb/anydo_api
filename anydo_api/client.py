#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from . import request
from .errors import *
from .constants import CONSTANTS
from .user import User

__all__ = ['Client']

class Client(object):
    """
    `Client` is the main interface for communication with an API.
    Responsible for authentication.
    """

    def __init__(self, email, password):
        self.session = self.__log_in(email, password)
        self.password = password

    def me(self, refresh=False):
        if not 'user' in self.__dict__ or refresh:
            data = request.get(
                url=CONSTANTS.get('ME_URL'),
                session=self.session
            )
            self.session.close()
            data.update({ 'password': self.password })
            self.password = None
            self.user = User(data_dict=data, session=self.session)

        return self.user

    def __log_in(self, email, password):
        credentials = {
            'j_username': email,
            'j_password': password,
            '_spring_security_remember_me': 'on'
        }

        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        session = requests.Session()

        response_obj = request.post(
            url=CONSTANTS.get('LOGIN_URL'),
            session=session,
            headers=headers,
            data=credentials,
            response_json=False
        )

        return session
