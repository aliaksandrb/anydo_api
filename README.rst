================================================================
anydo_api unofficial AnyDo API client for Python (v0.0.2 aplha)
================================================================

.. image:: https://img.shields.io/travis/aliaksandrb/anydo_api.svg
        :target: https://travis-ci.org/aliaksandrb/anydo_api

.. image:: https://img.shields.io/pypi/v/anydo_api.svg
        :target: https://pypi.python.org/pypi/anydo_api

.. image:: https://readthedocs.org/projects/anydo-api/badge/?version=latest
        :target: http://anydo-api.readthedocs.org/en/latest/

This simple client library provides access to basic features of `AnyDo <http://www.any.do/>`_ task manager in a
easy and object-oriented style.

It could be used for own projects integration's or as a tool for migration from one task manager to another.

Supported Features
------------------
* User CRUD operations
* Personal tasks CRUD and sharing
* Personal lists(categories) CRUD

Requirements
------------
* Automatically testing for `Python 2.7` and `Python 3.4`.
* Uses `requests>=2.8.0` for remote API calls.

Install
--------
::

$ pip install anydo_api

or directly from the repository:
::

$ git clone https://github.com/aliaksandrb/anydo_api
$ cd anydo_api
$ python setup.py install

Usage & examples:
-------------------
Currently not all functionality from the original `Chrome/Android/..` clients are supported.
Some of them just have no sense for console client, some just not ready yet :)

Here is what we have for now:

User management:
^^^^^^^^^^^^^^^^^
>>> from anydo_api.client import Client

**Create totally new user:**

>>> user = Client.create_user(name='Garlic', email='name@garlic.com', password='password')

**Access to its attributes both ways:**

>>> user['name'] # > 'Garlic'
>>> user.email # > 'name@garlic.com'

**Change the name:**

>>> user['name'] = 'Tomato'
>>> user.save() # changes are pushed to server
>>> user['name'] # > 'Tomato'

**Login with existent account:**

>>> user = Client(email='name@garlic.com', password='password').get_user()
>>> user['name'] # > 'Tomato'

**Get the possible updates from the server (in case if user was already instantiated but changed by other client/app)**

>>> user.refresh()

**Delete your account completely. Warning! Can't be undone:**

>>> user.destroy()
...

Tasks management:
^^^^^^^^^^^^^^^^^
>>> from anydo_api.client import Client
>>> from anydo_api.task import Task

>>> user = Client(email='name@garlic.com', password='password').get_user()

**List tasks:**

>>> user.tasks() # > []

**Create a new task:**

>>> task = Task.create(
               user=user,
               title='Clean garden',
               priority='High',
               category='Personal',
               repeatingMethod='TASK_REPEAT_OFF')

>>> task['assignedTo'] # > 'name@garlic.com'
>>> task.status # > 'UNCHECKED'

**Add note for task:**

>>> task.add_note('first task')
>>> task.notes() # > ['first task']

**Add a subtasks:**

>>> subtask = Task.create(user=user, title='Find a water', priority='Normal')
>>> task.add_subtask(subtask)
>>> subtask.parent()['title'] # > 'Clean garden'
>>> task.subtasks()[0]['title'] # > 'Find a water'

**Check the task:**

>>> subtask['status'] # > 'UNCHECKED'
>>> subtask.check()
>>> subtask['status'] # > 'CHECKED'

**Delete the task:**

>>> subtask.destroy()
>>> len(user.tasks()) # > 2
>>> len(user.tasks(refresh=True)) # > 1
...

Lists(categories) management:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>>> from anydo_api.client import Client
>>> from anydo_api.category import Category
>>> from anydo_api.task import Task

>>> user = Client(email='name@garlic.com', password='password').get_user()

**List categories:**

>>> list(map(lambda category: category['name'], user.categories())) # > ['GROCERY LIST', 'PERSONAL ERRANDS']

**Create a new category:**

>>> category = Category.create(user=user, name='Home')
>>> list(map(lambda category: category['name'], user.categories(refresh=True)))
# > ['GROCERY LIST', 'PERSONAL ERRANDS', 'Home']

**List category tasks:**

>>> category.tasks() # > []
>>> task = Task.create(user=user, title='In new category', priority='Normal')
>>> category.add_task(task)
>>> category.tasks()[0]['title'] # > 'In new category'

**Make category default one, for new tasks:**

>>> category.default # > False
>>> category.mark_default()
>>> category.default # > True

**Delete the category:**

>>> category.destroy()
>>> list(map(lambda category: category['name'], user.categories(refresh=True)))
# > ['GROCERY LIST', 'PERSONAL ERRANDS']
...

& More complex example, task sharing:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Assume we have two users: `Paca` and `Vaca`.
User `Paca` has a one task it wants to share with `Vaca`.

>>> task = paca.tasks()[0]
>>> task['title'] # > 'Paca Task'
>>> task.members() # > [{'paca@garlic.com': 'Paca'}]

**Share task with user:**

>>> task.share_with(vaca)

**Until task isn't approved it isn't shared:**

>>> vaca.tasks() # > []
>>> vaca.pending_tasks()
# > [{'id': 'm8cEmJJFXgYWrr3Xplj9zw==', 'invitedBy': {'name': 'Paca', 'email': 'paca@garlic.com', 'picture': None}, 'message': None, 'title': 'Paca Task'}]

**Approve the pending task:**

>>> vaca.approve_pending_task(pending_task=vaca.pending_tasks()[0])

**And now it is shared:**

>>> vaca.tasks()[0]['title'] # > 'Paca Task'

>>> task.members()
[{'paca@garlic.com': 'Paca'}, {'vaca@garlic.com': 'vaca@garlic.com'}]
...

For other methods and full support API check the docs or source code..

Contributions
-------------

Feedback, issue reports and feature/pull requests are greatly appreciated!
You could post them `into issues <https://github.com/aliaksandrb/anydo_api/issues>`_.

Generic guide for contributions is placed `here <https://github.com/aliaksandrb/anydo_api/blob/master/CONTRIBUTING.rst>`_.

Thanks!

* MIT license
* Automaticaly generated documentation: http://anydo-api.readthedocs.org/en/latest/.
