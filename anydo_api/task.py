#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import base64

from . import errors
from .constants import CONSTANTS

class Task(object):
    """
    `Task` is the class representing user task object.
    It wraps task-related JSON into class instances and
    responsible for task management.
    """

    def __init__(self, user, data_dict):
        self.user = user
        self.data_dict = data_dict
        self.is_dirty = False

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

    def save(self):
        """
        Pushes updated attributes to the server.
        If nothing was changed we dont hit an API.
        """

        if self.is_dirty:
            headers = {
                'Content-Type' : 'application/json',
                'Accept-Encoding': 'deflate'
            }

            response_obj = self.user.session.put(
                CONSTANTS.get('TASKS_URL') + '/' + self.id,
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































































































































