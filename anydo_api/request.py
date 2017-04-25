#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
anydo_api.request.

Helper functions for HTTP API calls.
Wrapped `requests` methods with default headers and options.
"""

import requests

from anydo_api import errors

__all__ = ('get', 'post', 'put', 'delete')

try:
    __SERVER_ERRORS = xrange(500, 600) # pylint: disable=undefined-variable
except NameError:
    __SERVER_ERRORS = range(500, 600)

def get(url, **options):
    """Simple GET request wrapper."""
    return __base_request(method='get', url=url, **options)

def post(url, **options):
    """Simple POST request wrapper."""
    return __base_request(method='post', url=url, **options)

def put(url, **options):
    """Simple PUT request wrapper."""
    return __base_request(method='put', url=url, **options)

def delete(url, **options):
    """Simple DELETE request wrapper."""
    return __base_request(method='delete', url=url, **options)


def __prepare_request_arguments(**options):
    """Return a dict representing default request arguments."""
    options = options.copy()

    headers = {
        'Content-Type'   : 'application/json',
        'Accept'         : 'application/json',
        'Accept-Encoding': 'deflate',
    }

    params = options.pop('params') if 'params' in options else ''
    timeout = options.pop('timeout') if 'timeout' in options else 5 # don't hung the client to long

    if 'headers' in options:
        headers.update(options.pop('headers'))

    request_arguments = {
        'headers': headers,
        'params' : params,
        'timeout': timeout,
    }

    request_arguments.update(options)
    return request_arguments

def __check_response_for_errors(response):
    """Raise and exception in case of HTTP error during API call, mapped to custom errors."""
    # bug in PyLint, seems not merged in 1.5.5 yet https://github.com/PyCQA/pylint/pull/742
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
        # should we skip original cause of exception or not?
        client_error.__cause__ = None
        raise client_error

def __base_request(method, url, session=None, **options):
    """
    Base request wrapper.

    Make request according to the `method` passed, with default options applied.
    Forward other arguments into `request` object from the `request` library.
    """
    response_json = options.pop('response_json') if 'response_json' in options else True
    if not session:
        session = requests.Session()
    request_arguments = __prepare_request_arguments(**options)

    if method == 'get':
        adapter = requests.packages.urllib3.util.Retry(total=2, status_forcelist=__SERVER_ERRORS)

        session.mount('http://', requests.adapters.HTTPAdapter(max_retries=adapter))
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=adapter))

    response = getattr(session, method)(url, **request_arguments)
    session.close()
    __check_response_for_errors(response)

    if response_json and method != 'delete':
        return response.json()

    return response
