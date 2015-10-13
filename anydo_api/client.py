#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json

SERVER_API_URL = 'https://sm-prod2.any.do'

CONSTANTS = {
    'SERVER_API_URL': SERVER_API_URL,
    'LOGIN_URL': SERVER_API_URL + '/j_spring_security_check',
    'ME_URL': SERVER_API_URL + '/me',
}

class Error(Exception): pass
class ClientError(Error): pass
class Unauthorized(ClientError): pass

class Client(object):
    """
    `Client` is the main interface for communication with an API.
    Responsible for authentication and user management.
    """

    @classmethod
    def log_in(klass, email, password):
        credentials = {
            'j_username': email,
            'j_password': password,
            '_spring_security_remember_me': 'on'
        }

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': None
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
            client_error = Unauthorized(error)
            client_error.__cause__ = None
            raise client_error
        finally: session.close()

        return session#klass.me(session)

    @classmethod
    def me(klass, session):
        user = session.get(CONSTANTS.get('ME_URL'))
        session.close()
        return user.json()
