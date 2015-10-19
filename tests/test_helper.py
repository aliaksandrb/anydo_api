#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vcr
import json

vcr = vcr.VCR(
    serializer='json',
    cassette_library_dir='tests',
)

def credentials_file():
    credentials_file = 'test_credentials.json'

    try:
        with open(credentials_file) as f:
            credentials = json.load(f)
    except FileNotFoundError as e:
        error = FileNotFoundError('{} file is required for remote API testing'
            .format(credentials_file))
        error.__cause__ = e
        raise error
    except ValueError as e:
        error = ValueError('{} file is bad formatted'.format(credentials_file))
        error.__cause__ = e
        raise error

    if len([item for item in credentials.items() if item[0] in ('username', 'password', 'email')
                                                    and item[1] != '']) < 3:
        raise ValueError('{} file has missed required keys or values'.format(credentials_file))

    return credentials

def scrub_string(string, replacement='******'):
    def before_record_response(response):
        try:
            text = response['body']['string'].decode('utf-8')
        except (KeyError, TypeError, UnicodeDecodeError):
            # pass
            # skip binary answers for now
            response['body']['string'] = ''
        else:
            if text:
                text.replace(string, replacement)
                text_dict = json.loads(text)
                text_dict['auth_token'] = replacement
                response['body']['string'] = json.dumps(text_dict).encode('utf-8')

        return response
    return before_record_response

