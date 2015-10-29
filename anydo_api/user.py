#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import request
from . import errors
from .constants import CONSTANTS
from .resource import Resource
from .task import Task
from .category import Category

__all__ = ['User']

class User(Resource):
    """
    `User` is the class representing User object.
    It wraps user-related JSON into class instances and
    responsible for user management.
    """

    _endpoint = CONSTANTS.get('ME_URL')
    _reserved_attrs = ('data_dict', 'session_obj', 'is_dirty')
    __alternate_endpoint = CONSTANTS.get('USER_URL')

    def __init__(self, data_dict, session):
        super(User, self).__init__(data_dict)
        self.session_obj = session

    def save(self):
        """
        Pushes updated attributes to the server.
        If nothing was changed we dont hit the API.
        """
        super(User, self).save(alternate_endpoint=CONSTANTS.get('ME_URL'))

    def session(self):
        """
        Shortcut to retrive object session for requests.
        """
        return self.session_obj

    def destroy(self):
        """
        Hits the API to destroy the user.
        Passes a changed alternate endpoint as it is differ from the class one.
        """
        super(User, self).destroy(alternate_endpoint=self.__alternate_endpoint)

    def tasks(self, refresh=False,
        include_deleted=False,
        include_done=False,
        include_checked=True,
        include_unchecked=True
    ):
        """
        Returns a remote or chached task list for user.
        """

        if not 'tasks_list' in self.__dict__ or refresh:
            params = {
                'includeDeleted': str(include_deleted).lower(),
                'includeDone': str(include_done).lower(),
            }

            tasks_data = request.get(
                url=CONSTANTS.get('TASKS_URL'),
                session=self.session(),
                params=params
            )

            self.tasks_list = [ Task(data_dict=task, user=self) for task in tasks_data ]

        self.tasks_list

        return Task.filter_tasks(self.tasks_list,
                include_deleted=include_deleted,
                include_done=include_done,
                include_checked=include_checked,
                include_unchecked=include_unchecked
        )

    def categories(self, refresh=False, include_deleted=False):
        """
        Returns a remote or chached categories list for user.
        """
        if not 'categories_list' in self.__dict__ or refresh:
            params = {
                'includeDeleted': str(include_deleted).lower(),
            }

            categories_data = request.get(
                url=CONSTANTS.get('CATEGORIES_URL'),
                params=params
            )

            self.categories_list = [ Category(data_dict=category, user=self) for category in categories_data ]

        result = self.categories_list
        if not include_deleted:
            result = list(filter(lambda cat: not cat['isDeleted'], result))

        return result

    def add_task(self, task):
        """
        Adds new task into internal storage.
        """

        if 'tasks_list' in self.__dict__:
            self.tasks_list.append(task)
        else:
            self.tasks_list = [task]

    def add_category(self, category):
        """
        Adds new category into internal storage.
        """

        if 'categories_list' in self.__dict__:
            self.categories_list.append(category)
        else:
            self.categories_list = [category]

    def default_category(self):
        """
        Returns defaul category for user if exist
        """
        return next((cat for cat in self.categories() if cat.isDefault), None)

    def pending_tasks(self, refresh=False):
        """
        Returns a list of dicts representing a pending task that was shared with current user.
        Empty list otherwise.
        """
        if not '_pending_tasks' in self.__dict__ or refresh:
            response_obj = request.get(
                url=self.__class__._endpoint + '/pending',
                session=self.session()
            )

            self._pending_tasks = response_obj['pendingTasks']

        return self._pending_tasks or []

    def pending_tasks_ids(self, refresh=False):
        """
        Returns a list of pending tasks ids shared with user.
        Empty list otherwise.
        """
        return [task['id'] for task in self.pending_tasks(refresh=refresh)]

    def approve_pending_task(self, pending_task_id=None, pending_task=None):
        """
        Approves pending task via API call.
        Accept pending_task_id or pending_task dict (in format of pending_tasks.
        """
        task_id = pending_task_id or pending_task['id']
        if not task_id:
            raise errors.AttributeError('Eather :pending_task_id or :pending_task argument is required.')

        response_obj = request.post(
            url=self.__class__._endpoint + '/pending/' + task_id + '/accept',
            session=self.session()
        )

        return response_obj

    @staticmethod
    def required_attributes():
        """
        Returns a set of required fields for valid user creation.
        This tuple is checked to prevent unnecessary API calls.
        """

        return {'name', 'email', 'password'}

    @classmethod
    def create(klass, **fields):
        """
        Creates new user by required parameters
        """
        klass.check_for_missed_fields(fields)

        json_data = {
            'name': fields.get('name'),
            'username': fields.get('email'),
            'password': fields.get('password'),
            'emails': fields.get('emails', fields.get('email')),
            'phoneNumbers': fields.get('phone_numbers', [])
        }

        request.post(
            url=klass.__alternate_endpoint,
            json=json_data
        )

        from .client import Client
        user = Client(email=fields.get('email'), password=fields.get('password')).me()
        return user

