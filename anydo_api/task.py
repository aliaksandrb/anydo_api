#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import base64
import random
import time

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

    def session(self):
        return self.user.session

    @staticmethod
    def generate_uid():
        random_string = ''.join([chr(random.randint(0, 255)) for _ in range(0, 16)])
        try:
            random_string = random_string.encode('utf-8')
        except UnicodeDecodeError: pass

        result = base64.urlsafe_b64encode(random_string)
        try:
            result = result.decode('utf-8')
        except UnicodeDecodeError: pass

        return result

    @classmethod
    def create(klass, user, **kwargs):
        """
        Creates new task with required parameters
        """

        headers = {
            'Content-Type'   : 'application/json',
            'Accept'         : 'application/json',
            'Accept-Encoding': 'deflate',
        }

        json_data = kwargs.copy()
        json_data.update({ 'id': klass.generate_uid() })
#        params = {
#            'includeDeleted': 'false',
#            'includeDone'   : 'false',
#            'responseType'  : 'flat'
#        }

        response_obj = user.session.post(
            CONSTANTS.get('TASKS_URL'),
            json=[json_data],
            headers=headers,
#            params=params
        )
        #defaults: function() {
        #        var a = (new Date).getTime();
        #        return {
        #            title: null,
        #            status: TaskStatus.UNCHECKED,
        #            repeatingMethod: TASK_REPEAT.TASK_REPEAT_OFF,
        #            shared: !1,
        #            priority: TaskPriority.Normal,
        #            creationDate: a,
        #            taskExpanded: !1
        #            }
        #        }
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
        finally: user.session.close()

        task = Task(user, response_obj.json())
        return task

