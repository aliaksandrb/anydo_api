#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vcr
import json
import os

vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='tests',
)

def credentials_values():
    """Load from environment valid AnyDo credentials required for authentication."""
    credentials = {
        'username': os.environ.get('ANYDO_USERNAME'),
        'password': os.environ.get('ANYDO_PASSWORD'),
        'email': os.environ.get('ANYDO_EMAIL')
    }

    if not all(list(credentials.values())):
        raise ValueError('Missed required credentials in current environment!')

    return credentials

def scrub_string(string, replacement='******'):
    """
    Decorator for scrubbing sensative data like passwords or auth-keys.
    """
    def before_record_response(response):
        try:
            text = response['body']['string'].decode('utf-8')
        except (KeyError, TypeError, UnicodeDecodeError):
            # pass
            # skip binary answers for now, as they are not json serializable.
            response['body']['string'] = ''
        else:
            if text:
                text.replace(string, replacement)
                text_dict = json.loads(text)
                text_dict['auth_token'] = replacement
                response['body']['string'] = json.dumps(text_dict).encode('utf-8')

        return response
    return before_record_response

