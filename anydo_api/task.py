#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`anydo_api.task`.

`Task` class.
"""

from anydo_api import request
from anydo_api.constants import CONSTANTS, TASK_STATUSES
from anydo_api.resource import Resource

__all__ = ('Task')

class Task(Resource):
    """
    `Task` is the class representing user task object.

    It wraps task-related JSON into class instances and responsible for task management.
    """

    _endpoint = CONSTANTS.get('TASKS_URL')
    _reserved_attrs = ('user', 'data_dict', 'is_dirty')

    def __init__(self, data_dict, user):
        """Constructor for Task."""
        super(Task, self).__init__(data_dict)
        self.user = user

    def check(self):
        """
        Mark task as CHECKED.

        Using update functionality under the hood.
        """
        self['status'] = 'CHECKED'
        self.is_dirty = True
        self.save()

    def done(self):
        """
        Mark task as DONE.

        Using update functionality under the hood.
        """
        self['status'] = 'DONE'
        self.save()

    def session(self):
        """Shortcut to retrive user session for requests."""
        return self.user.session()

    def subtasks(self):
        """Return a list with subtasks of current task for same user."""
        return [task for task in self.user.tasks() if task['parentGlobalTaskId'] == self['id']]

    def create_subtask(self, **fields):
        """Create a new tasks from provided fields and makes it an subtask of current one."""
        subtask_attrs = fields.copy()
        subtask_attrs.update({'parentGlobalTaskId': self['id']})
        subtask = Task.create(user=self.user, **subtask_attrs)
        self.user.add_task(subtask)
        return subtask

    def add_subtask(self, subtask):
        """
        Add subtask to current task.

        Change synhronized remotly.
        """
        # Currently we don't support task reassignment from one user to another
        subtask['parentGlobalTaskId'] = self['id']
        subtask.save()

    def notes(self):
        """Return a parsed list of notes for the task."""
        if self.note:
            return [note for note in self.note.split('\n') if note]

        return []

    def add_note(self, text_note):
        """Add a text note to current task.

        Change synhronized remotly.
        """
        note = self['note'] or ''
        if not note.endswith('\n'):
            note = note + '\n'
        self['note'] = note + text_note
        self.save()

    def members(self):
        """
        Return a list of dicts {username:email} representing the task members, including owner.

        If the task is not share returns only owner info.
        """
        objects_list = self['sharedMembers']
        if objects_list:
            return [{member['target']: member['name']} for member in objects_list]

        return [{self.user['email']: self.user['name']}]

    def share_with(self, new_member, message=None):
        """
        Share a task with new member.

        Pushes changes to server.
        Updates task members list and new member tasks list.
        """
        json_data = {
            'invitees': [{'email': new_member['email']}],
            'message': message
        }

        response_obj = request.post(
            url=self.get_endpoint() + '/' + self['id'] + '/share',
            json=json_data,
            session=self.session()
        )

        self.data_dict = response_obj

        return self

    def category(self):
        """Return a category object based mapped to selected task."""
        return next(
            (cat for cat in self.user.categories() if cat['id'] == self['categoryId']),
            None
        )

    def parent(self):
        """Return parent task object for subtask and None for first-level task."""
        return next(
            (task for task in self.user.tasks() if task['id'] == self['parentGlobalTaskId']),
            None
        )

    @staticmethod
    def required_attributes():
        """
        Return a set of required fields for valid task creation.

        This tuple is checked to prevent unnecessary API calls.

        Seems that :id and :title attributes are required for now, where
        :id is set automatically.
        """
        return {'title'}

    @staticmethod
    def filter_tasks(tasks_list, **filters):
        """
        Filter tasks by their status.

        Returns a new filtered list.
        """
        result = tasks_list[:]
        statuses = list(TASK_STATUSES)

        if not filters.get('include_deleted', False):
            statuses.remove('DELETED')
        if not filters.get('include_done', False):
            statuses.remove('DONE')
        if not filters.get('include_checked', False):
            statuses.remove('CHECKED')
        if not filters.get('include_unchecked', False):
            statuses.remove('UNCHECKED')

        result = [task for task in result if task['status'] in statuses]
        return list(result)


    @classmethod
    def _create_callback(cls, resource_json, user):
        """
        Callback method that is called automaticly after each successfull creation via remote API.

        Return an task instance.
        """
        task = cls(data_dict=resource_json[0], user=user)
        user.add_task(task)

        return task
