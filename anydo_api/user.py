#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from . import errors
from .constants import CONSTANTS

from .task import Task

class User(object):
    """
    `User` is the class representing User object.
    It wraps user-related JSON into class instances and
    responsible for user management.
    """

    __reserved_attrs = ('data_dict', 'session', 'is_dirty')

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

    def tasks(self, refresh=False,
        include_deleted=False,
        include_done=False,
        include_checked=True,
        include_unchecked=True
    ):
        if not 'tasks_list' in self.__dict__ or refresh:
            params = {
                'includeDeleted': str(include_deleted).lower(),
                'includeDone': str(include_done).lower(),
            }

            tasks_data = self.session.get(
                CONSTANTS.get('TASKS_URL'),
                headers={
                    'Content-Type': 'application/json',
                    'Accept-Encoding': 'deflate'
                },
                params=params
            ).json()
            self.session.close()

            self.tasks_list = [ Task(user=self, data_dict=task) for task in tasks_data ]

        self.tasks_list

        return Task.filter_tasks(self.tasks_list,
                include_deleted=include_deleted,
                include_done=include_done,
                include_checked=include_checked,
                include_unchecked=include_unchecked
        )

    def add_task(self, task):
        """
        Adds new task into internal storage.
        """

        if 'tasks_list' in self.__dict__:
            self.tasks_list.append(task)
        else:
            self.tasks_list = [task]

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
            super(User, self).__setattr__(attr, new_value)

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

