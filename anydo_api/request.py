#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json

from . import errors

__all__ = ['get', 'post', 'put', 'delete']

def __base_request(method, url, session=None, **options):
    options = options.copy()

    default_headers = {
        'Content-Type'   : 'application/json',
        'Accept'         : 'application/json',
        'Accept-Encoding': 'deflate',
    }
    headers = default_headers

    session = options.pop('session') if 'session' in options else requests.Session()
    params = options.pop('params') if 'params' in options else ''
    response_json = options.pop('response_json') if 'response_json' in options else True

    if 'headers' in options:
        headers.update(options.pop('headers'))

    request_arguments = {
        'url'    : url,
        'headers': headers,
        'params' : params,
    }

    request_arguments.update(options)
    response = getattr(session, method)(**request_arguments)

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
    finally: session.close()

    return response.json() if response_json else response

def get(url, **options):
    return __base_request(method='get', url=url, **options)

def post(url, **options):
    return __base_request(method='post', url=url, **options)

def put(url, **options):
    return __base_request(method='put', url=url, **options)

def delete():pass
