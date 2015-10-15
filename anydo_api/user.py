#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from .errors import *
from .constants import CONSTANTS

class User(object):
    """
    `User` is the class representing User object.
    It wraps user-related JSON into class instances and
    responsible for user management.
    """

    def __init__(self, data_dict):
        self.data = data_dict

    @classmethod
    def create(klass, name, email, password, emails=None, phone_numbers=[]):
        """
        Creates new user by required parameters
        """
        headers = {
            'Content-Type' : 'application/json',
        }

        json_data = {
            'name': name,
            'username': email,
            'password': password,
            'emails': emails or email,
            'phoneNumbers': phone_numbers
        }

        # session
        response_obj = requests.post(
            CONSTANTS.get('USER_URL'),
            json=json_data,
            headers=headers
        )

        try:
            response_obj.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response_obj.status_code == 400:
                client_error = BadRequestError(response_obj.content)
            elif response_obj.status_code == 409:
                client_error = ConflictError(response_obj.content)
            else:
                client_error = InternalServerError(error)

            client_error.__cause__ = None
            raise client_error

       # catch possible exceptions
        return klass(data_dict=response_obj.json())

