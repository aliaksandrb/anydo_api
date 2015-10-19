#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import base64

from . import errors
from .constants import CONSTANTS

class User(object):
    """
    `User` is the class representing User object.
    It wraps user-related JSON into class instances and
    responsible for user management.
    """

    def __init__(self, session, data_dict):
        self.data_dict = data_dict
        self.session = session
        self.is_dirty = False

    def save(self):
        """
        Pushes updated attributes to the server.
        If nothing was changed we dont hit an API.
        """

        if self.is_dirty:
            headers = {
                'Content-Type' : 'application/json',
            }

            response_obj = self.session.put(
                CONSTANTS.get('ME_URL'),
                json=self.data_dict,
                headers=headers
            )

            try:
                response_obj.raise_for_status()
            except requests.exceptions.HTTPError as error:
                if response_obj.status_code == 400:
                    client_error = errors.BadRequestError(response_obj.content)
                elif response_obj.status_code == 409:
                    client_error = errors.ConflictError(response_obj.content)
                else:
                    client_error = errors.InternalServerError(error)

                client_error.__cause__ = None
                raise client_error

        self.is_dirty = False
        return self

    def destroy(self):
        """
        Hits the API to destroy the user.
        """

        headers = {
            'Content-Type': 'application/json',
            'AnyDO-Puid': str(self.data_dict['id'])
        }

        response_obj = self.session.delete(
            CONSTANTS.get('USER_URL'),
            json={ 'email': self.email, 'password': self.password },
            headers=headers
        )

        try:
            response_obj.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response_obj.status_code == 400:
                client_error = errors.BadRequestError(response_obj.content)
            elif response_obj.status_code == 409:
                client_error = errors.ConflictError(response_obj.content)
            else:
                client_error = errors.InternalServerError(error)

            client_error.__cause__ = None
            raise client_error

        return self

    def __getitem__(self, key):
        return self.data_dict[key]

    def __getattr__(self, attr):
        try:
            result = self.data_dict[attr]
        except KeyError:
            raise errors.AttributeError(attr + ' is not exist')

        return result

    def __setitem__(self, attr, new_value):
        if attr in self.data_dict:
            old_value = self.__dict__['data_dict'][attr]

            if old_value != new_value:
                self.__dict__['data_dict'][attr] = new_value
                self.is_dirty = True
        else:
            raise errors.AttributeError(attr + ' is not exist')

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

        session = requests.Session()
        response_obj = session.post(
            CONSTANTS.get('USER_URL'),
            json=json_data,
            headers=headers
        )

        try:
            response_obj.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if response_obj.status_code == 400:
                client_error = errors.BadRequestError(response_obj.content)
            elif response_obj.status_code == 409:
                client_error = errors.ConflictError(response_obj.content)
            else:
                client_error = errors.InternalServerError(error)

            client_error.__cause__ = None
            raise client_error
        finally: session.close()

       # catch possible exceptions
        from .client import Client
        user = Client(email=email, password=password).me()
        return user

