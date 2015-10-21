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

    __reserved_attrs = ('user', 'data_dict', 'is_dirty')

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
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.is_dirty = True
        else:
            raise errors.AttributeError(attr + ' is not exist')

    def __setattr__(self, attr, new_value):
        if attr not in self.__class__.__reserved_attrs and attr in self.data_dict:
            old_value = self.data_dict[attr]

            if old_value != new_value:
                self.data_dict[attr] = new_value
                self.__dict__['is_dirty'] = True
        else:
            super(Task, self).__setattr__(attr, new_value)

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

            response_obj = self.session().put(
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

    def destroy(self):
        """
        Deletes the tasks by remote API call
        """
        headers = {
            'Content-Type': 'application/json',
        }

        response_obj = self.session().delete(
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

        return self

    delete = destroy

    def check(self):
        """
        Marks task as CHECKED.
        Uses update functionality under the hood.
        """
        self.status = 'CHECKED'
        self.is_dirty = True
        self.save()

    def done(self):
        """
        Marks task as DONE.
        Uses update functionality under the hood.
        """
        self['status'] = 'DONE'
        self.save()

    def session(self):
        """
        Chortcut to retrive user session for requests.
        """
        return self.user.session

    def subtasks(self):
        """
        Returns a list with subtasks of current task for same user.
        """
        return [task for task in self.user.tasks() if task['parentGlobalTaskId'] == self['id']]

    def create_subtask(self, **fields):
        """
        Creates a new tasks from provided fields and makes it an subtask of current one.
        """
        subtask_attrs = fields.copy()
        subtask_attrs.update({ 'parentGlobalTaskId': self['id'] })
        subtask = Task.create(user=self.user, **subtask_attrs)
        self.user.add_task(subtask)
        return subtask

    def add_subtask(self, subtask):
        """
        Adds subtask to current task.
        Change synhronized remotly.
        """
        # Currently we don't support task reassignment from one user to another
        subtask['parentGlobalTaskId'] = self['id']
        subtask.save()

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

    @staticmethod
    def required_attributes():
        """
        Returns a set of required fields for valid task creation.
        This tuple is checked to prevent unnecessary API calls.

        Seems that :id and :title attributes are required for now, where
        :id is set automatically.
        """

        return {'title'}

    @classmethod
    def check_for_missed_fields(klass, fields):
        """
        Checks task attributes for missed required.
        Raises exception with a list of all missed.
        """

        missed = klass.required_attributes() - set(fields.keys())
        if len(missed) > 0:
            raise errors.AttributeError('Missing required fields: {}!'.format(missed))

    @classmethod
    def create(klass, user, **fields):
        """
        Creates new task via API call.
        """

        klass.check_for_missed_fields(fields)

        headers = {
            'Content-Type'   : 'application/json',
            'Accept'         : 'application/json',
            'Accept-Encoding': 'deflate',
        }

        json_data = fields.copy()
        json_data.update({ 'id': klass.generate_uid() })
        params = {
            'includeDeleted': 'false',
            'includeDone'   : 'false',
#            'responseType'  : 'flat'
        }

        response_obj = user.session.post(
            CONSTANTS.get('TASKS_URL'),
            json=[json_data],
            headers=headers,
            params=params
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
        finally: user.session.close()

        task = Task(user, data_dict=response_obj.json()[0])
        user.add_task(task)
        return task

