#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

SERVER_API_URL = 'https://sm-prod2.any.do'

CONSTANTS = {
    'SERVER_API_URL': SERVER_API_URL,
    'LOGIN_URL': SERVER_API_URL + '/j_spring_security_check',
    'ME_URL': SERVER_API_URL + '/me',
    'USER_URL': SERVER_API_URL + '/user',
}

class Error(Exception): pass
class ClientError(Error): pass

class UnauthorizedError(ClientError): pass
class BadRequestError(ClientError): pass
class InternalServerError(ClientError): pass
class ConflictError(ClientError): pass

class Client(object):
    """
    `Client` is the main interface for communication with an API.
    Responsible for authentication.
    """

    def __init__(self, email, password):
        self.session = self.__log_in(email, password)

    def me(self):
        user = self.session.get(CONSTANTS.get('ME_URL'))
        self.session.close()
        return user.json()

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
