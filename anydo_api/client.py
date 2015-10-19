#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from .errors import *
from .constants import CONSTANTS
from .user import User

class Client(object):
    """
    `Client` is the main interface for communication with an API.
    Responsible for authentication.
    """

    def __init__(self, email, password):
        self.session = self.__log_in(email, password)
        self.password = password

    def me(self, refresh=False):
        if not hasattr(self, 'user') or refresh:
            data = self.session.get(CONSTANTS.get('ME_URL')).json()
            self.session.close()
            data.update({ 'password': self.password })
            self.password = None
            self.user = User(session=self.session, data_dict=data)

        return self.user

    def __log_in(self, email, password):
        credentials = {
            'j_username': email,
            'j_password': password,
            '_spring_security_remember_me': 'on'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': None # Why AnyDo says that gzipped but actually not?
        }

        session = requests.Session()

        response_obj = session.post(
            CONSTANTS.get('LOGIN_URL'),
            data=credentials,
            headers=headers
        )

        try:
            response_obj.raise_for_status()
        except requests.exceptions.HTTPError as error:
            client_error = UnauthorizedError(error)
            client_error.__cause__ = None
            raise client_error
        finally: session.close()

        return session
