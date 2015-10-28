#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json

from .errors import *

__all__ = ['get', 'post', 'put', 'delete']

def __base_request(method, url, session=None, **options):
    options = options.copy()

    default_headers = {
        'Content-Type'   : 'application/json',
        'Accept'         : 'application/json',
        'Accept-Encoding': 'deflate',
    }

    session = options.pop('session') if 'headers' in options else requests.Session()
    headers = options.pop('headers') if 'headers' in options else default_headers
    params = options.pop('params') if 'params' in options else ''

    response = getattr(session, method)(
        url,
        headers=headers,
        params=params
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        if response.status_code == 400:
            client_error = errors.BadRequestError(response.content)
        elif response.status_code == 409:
            client_error = errors.ConflictError(response.content)
        else:
            client_error = errors.InternalServerError(error)

        client_error.__cause__ = None
        raise client_error
    finally: session.close()

    return response.json()

def get(url, **options):
    return __base_request(method='get', url=url, **options)

def post():pass
def put():pass
def delete():pass
