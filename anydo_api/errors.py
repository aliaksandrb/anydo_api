#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Error(Exception): pass

class ClientError(Error): pass
class ModelError(Error): pass

class UnauthorizedError(ClientError): pass
class BadRequestError(ClientError): pass
class InternalServerError(ClientError): pass
class ConflictError(ClientError): pass

class AttributeError(ModelError): pass
class NotImplemented(ModelError): pass

