#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
`Client` is the main interface for communication with an API.

Responsible for authentication and user management.
"""

import requests
import json

SERVER_API_URL = 'https://sm-prod2.any.do'

CONSTANTS = {
    'SERVER_API_URL': SERVER_API_URL,
    'LOGIN_URL': SERVER_API_URL + '/j_spring_security_check',}

class Error(Exception): pass
class ClientError(Error): pass
class Unauthorized(ClientError): pass

class Client(object):

    @classmethod
    def log_in(klass, username, password):
        credentials = {
            'j_username': username,
            'j_password': password,
            '_spring_security_remember_me': 'on'}

        #Session()
        response_obj = requests.post(CONSTANTS.get('LOGIN_URL'),
            json=credentials,
            headers={'content-type': 'application/x-www-form-urlencoded'})

        try:
            response_obj.raise_for_status()
            response_json = response_obj.json()
        except requests.exceptions.HTTPError as error:
            client_error = Unauthorized(error)
            client_error.__cause__ = None

            raise client_error

        return response_json

