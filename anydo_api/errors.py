#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`anydo_api.errors`.

`Errors` module.

Custom names for library dependent exceptions.
"""

__all__ = ('Error', 'ClientError', 'ModelError',
           'UnauthorizedError', 'BadRequestError', 'InternalServerError',
           'ConflictError', 'ModelAttributeError', 'MethodNotImplementedError')

class Error(Exception):
    """Base error class for library namespacing."""

    pass

class ClientError(Error):
    """API Client related errors."""

    pass

class ModelError(Error):
    """Resource models related errors."""

    pass

class UnauthorizedError(ClientError):
    """Invalid credentials error."""

    pass

class BadRequestError(ClientError):
    """BadRequest error remap."""

    pass

class InternalServerError(ClientError):
    """InternalServerError error remap."""

    pass

class ConflictError(ClientError):
    """Conflic error in case when user already exists."""

    pass

class ModelAttributeError(ModelError):
    """Model attribute is missed error."""

    pass

class MethodNotImplementedError(ModelError):
    """NotImplemented error remap for abstract Resource class."""

    pass
