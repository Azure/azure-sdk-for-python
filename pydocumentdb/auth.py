# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Authorization helper functions.
"""

from hashlib import sha256
import hmac

import pydocumentdb.http_constants as http_constants


def GetAuthorizationHeader(document_client,
                           verb,
                           path,
                           resource_id,
                           resource_type,
                           headers):
    """Gets the authorization header.

    :Parameters:
        - `document_client`: document_client.DocumentClient
        - `verb`: str
        - `path`: str
        - `resource_id`: str
        - `resource_type`: str
        - `headers`: dict

    :Returns:
        dict, the authorization headers.

    """
    if document_client.master_key:
        return __GetAuthorizationTokenUsingMasterKey(verb,
                                                    resource_id,
                                                    resource_type,
                                                    headers,
                                                    document_client.master_key)
    elif document_client.resource_tokens:
        return __GetAuthorizationTokenUsingResourceTokens(
            document_client.resource_tokens, path, resource_id)


def __GetAuthorizationTokenUsingMasterKey(verb,
                                         resource_id,
                                         resource_type,
                                         headers,
                                         master_key):
    """Gets the authorization token using `master_key.

    :Parameters:
        - `verb`: str
        - `resource_id`: str
        - `resource_type`: str
        - `headers`: dict
        - `master_key`: st

    :Returns:
        dict

    """
    key = master_key.decode('base64')

    text = ((verb or '') + '\n' +
            (resource_type or '') + '\n' +
            (resource_id or '') + '\n' +
            (headers[http_constants.HttpHeaders.XDate]
             if http_constants.HttpHeaders.XDate in headers else '') + '\n' +
            (headers[http_constants.HttpHeaders.HttpDate]
             if http_constants.HttpHeaders.HttpDate in headers else '') + '\n')

    body = text.lower().decode('utf8')

    hm = hmac.new(key, body, sha256)
    signature = hm.digest().encode('base64')

    master_token = 'master'
    token_version = '1.0'
    return 'type=' + master_token +'&ver=' + token_version + '&sig=' + signature[:-1]


def __GetAuthorizationTokenUsingResourceTokens(resource_tokens,
                                              path,
                                              resource_id):
    """Get the authorization token using `resource_tokens`.

    :Parameters:
        - `resource_tokens`: dict
        - `path`: str
        - `resource_id`: str

    :Returns:
        dict

    """
    if resource_id in resource_tokens and resource_tokens[resource_id]:
        return resource_tokens[resource_id]
    else:
        path_parts = path.split('/')
        resource_types = ['dbs', 'colls', 'docs', 'sprocs', 'udfs', 'triggers',
                          'users', 'permissions', 'attachments', 'media',
                          'conflicts']
        for one_part in reversed(path_parts):
            if not one_part in resource_types and one_part in resource_tokens:
                return resource_tokens[one_part]
        return None