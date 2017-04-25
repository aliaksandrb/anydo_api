#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`anydo_api.user`.

`User` class.
"""

from anydo_api import request
from anydo_api import errors
from anydo_api.category import Category
from anydo_api.constants import CONSTANTS
from anydo_api.resource import Resource
from anydo_api.task import Task

__all__ = ('User')

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
        """Constructor for User."""
        super(User, self).__init__(data_dict)
        self.session_obj = session
        self.categories_list = None
        self.tasks_list = None
        self._pending_tasks = None

    def save(self, alternate_endpoint=None):
        """
        Pushe updated attributes to the server.

        If nothing was changed we dont hit the API.
        """
        super(User, self).save(alternate_endpoint=self.get_endpoint())

    def session(self):
        """Shortcut to retrive object session for requests."""
        return self.session_obj

    def destroy(self, alternate_endpoint=None):
        """
        Hit the API to destroy the user.

        Pass a changed alternate endpoint as it is differ from the class one.
        """
        super(User, self).destroy(alternate_endpoint=self.__alternate_endpoint)

    delete = destroy

    def refresh(self, alternate_endpoint=None):
        """
        Reload resource data from remote API.

        Pass a changed alternate endpoint as it is differ from the class one.
        """
        super(User, self).refresh(alternate_endpoint=self.get_endpoint())

    # pylint: disable=too-many-arguments
    def tasks(self,
              refresh=False,
              include_deleted=False,
              include_done=False,
              include_checked=True,
              include_unchecked=True):
        """Return a remote or chached task list for user."""
        if not self.tasks_list or refresh:
            params = {
                'includeDeleted': str(include_deleted).lower(),
                'includeDone': str(include_done).lower(),
            }

            tasks_data = request.get(
                url=CONSTANTS.get('TASKS_URL'),
                session=self.session(),
                params=params
            )

            self.tasks_list = [Task(data_dict=task, user=self) for task in tasks_data]

        return Task.filter_tasks(self.tasks_list,
                                 include_deleted=include_deleted,
                                 include_done=include_done,
                                 include_checked=include_checked,
                                 include_unchecked=include_unchecked)

    def categories(self, refresh=False, include_deleted=False):
        """Return a remote or cached categories list for user."""
        if not self.categories_list or refresh:
            params = {
                'includeDeleted': str(include_deleted).lower(),
            }

            categories_data = request.get(
                url=CONSTANTS.get('CATEGORIES_URL'),
                session=self.session(),
                params=params
            )

            self.categories_list = [
                Category(data_dict=category, user=self) for category in categories_data
            ]

        result = self.categories_list
        if not include_deleted:
            result = [cat for cat in result if not cat['isDeleted']]

        return result

    def add_task(self, task):
        """Add new task into internal storage."""
        if self.tasks_list:
            self.tasks_list.append(task)
        else:
            self.tasks_list = [task]

    def add_category(self, category):
        """Add new category into internal storage."""
        if self.categories_list:
            self.categories_list.append(category)
        else:
            self.categories_list = [category]

    def default_category(self):
        """Return default category for user if exist."""
        return next((cat for cat in self.categories() if cat.isDefault), None)

    def pending_tasks(self, refresh=False):
        """
        Return a list of dicts representing a pending task that was shared with current user.

        Empty list otherwise.
        """
        if not self._pending_tasks or refresh:
            response_obj = request.get(
                url=self.get_endpoint() + '/pending',
                session=self.session()
            )

            self._pending_tasks = response_obj['pendingTasks']

        return self._pending_tasks or []

    def pending_tasks_ids(self, refresh=False):
        """
        Return a list of pending tasks ids shared with user.

        Empty list otherwise.
        """
        return [task['id'] for task in self.pending_tasks(refresh=refresh)]

    def approve_pending_task(self, pending_task_id=None, pending_task=None):
        """
        Approve pending task via API call.

        Accept pending_task_id or pending_task dict (in format of pending_tasks.
        """
        task_id = pending_task_id or pending_task['id']
        if not task_id:
            raise errors.ModelAttributeError(
                'Eather :pending_task_id or :pending_task argument is required.'
            )

        response_obj = request.post(
            url=self.get_endpoint() + '/pending/' + task_id + '/accept',
            session=self.session()
        )

        return response_obj

    @staticmethod
    def required_attributes():
        """
        Return a set of required fields for valid user creation.

        This tuple is checked to prevent unnecessary API calls.
        """
        return {'name', 'email', 'password'}
