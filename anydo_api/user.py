#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from .client import CONSTANTS, InternalServerError, BadRequest

class User(object):
    """
    `User` is the class representing User object.
    It wraps user-related JSON into class instances and
    responsible for user management.
    """

    @staticmethod
    def create(name, username, password, emails, phone_numbers=[]):
        headers = {
            'Content-Type' : 'application/json',
        }

        json_data = {
            'name': name,
            'username': username,
            'password': password,
            'emails': emails,
            'phoneNumbers': phone_numbers
        }

        response_obj = requests.post(
            CONSTANTS.get('USER_URL'),
            json=json_data,
            headers=headers
        )

        try:
            response_obj.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response_obj.status_code == 400:
                client_error = BadRequest(response_obj.content)
            else:
                client_error = InternalServerError(error)

            client_error.__cause__ = None
            raise client_error

        return response_obj.json()

