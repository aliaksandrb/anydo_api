#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from . import errors

__all__ = ['get', 'post', 'put', 'delete']

def get(url, **options):
    """
    Simple GET request wrapper.
    """
    return __base_request(method='get', url=url, **options)

def post(url, **options):
    """
    Simple POST request wrapper.
    """
    return __base_request(method='post', url=url, **options)

def put(url, **options):
    """
    Simple PUT request wrapper.
    """
    return __base_request(method='put', url=url, **options)

def delete(url, **options):
    """
    Simple DELETE request wrapper.
    """
    return __base_request(method='delete', url=url, **options)


def __prepare_request_arguments(**options):
    """
    Returns a dict representing default request arguments.
    """
    options = options.copy()

    headers = {
        'Content-Type'   : 'application/json',
        'Accept'         : 'application/json',
        'Accept-Encoding': 'deflate',
    }

    params = options.pop('params') if 'params' in options else ''

    if 'headers' in options:
        headers.update(options.pop('headers'))

    request_arguments = {
        'headers': headers,
        'params' : params,
    }

    request_arguments.update(options)
    return request_arguments

def __check_response_for_errors(response):
    """
    Raises and exception in case of HTTP error during API call, mapped to custom errors.
    """
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        if response.status_code == 400:
            client_error = errors.BadRequestError(response.content)
        elif response.status_code == 401:
            client_error = errors.UnauthorizedError(response.content)
        elif response.status_code == 409:
            client_error = errors.ConflictError(response.content)
        else:
            client_error = errors.InternalServerError(error)

        client_error.__cause__ = None
        raise client_error

def __base_request(method, url, session=None, **options):
    """
    Base request wrapper.
    Makes request according to the `method` passed, with default options applied.
    Forwards other arguments into `request` object from the `request` library.
    """
    response_json = options.pop('response_json') if 'response_json' in options else True
    session = options.pop('session') if 'session' in options else requests.Session()
    request_arguments=__prepare_request_arguments(**options)

    response = getattr(session, method)(url, **request_arguments)
    session.close()
    __check_response_for_errors(response)

    if response_json and method != 'delete':
        return response.json()

    return response
