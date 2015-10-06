# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Authorization helper functions.
"""

from hashlib import sha256
import hmac

import pydocumentdb.http_constants as http_constants


def GetAuthorizationHeader(document_client,
                           verb,
                           path,
                           resource_id_or_fullname,
                           resource_type,
                           headers):
    """Gets the authorization header.

    :Parameters:
        - `document_client`: document_client.DocumentClient
        - `verb`: str
        - `path`: str
        - `resource_id_or_fullname`: str
        - `resource_type`: str
        - `headers`: dict

    :Returns:
        dict, the authorization headers.

    """
    if document_client.master_key:
        return __GetAuthorizationTokenUsingMasterKey(verb,
                                                    resource_id_or_fullname,
                                                    resource_type,
                                                    headers,
                                                    document_client.master_key)
    elif document_client.resource_tokens:
        return __GetAuthorizationTokenUsingResourceTokens(
            document_client.resource_tokens, path, resource_id_or_fullname)


def __GetAuthorizationTokenUsingMasterKey(verb,
                                         resource_id_or_fullname,
                                         resource_type,
                                         headers,
                                         master_key):
    """Gets the authorization token using `master_key.

    :Parameters:
        - `verb`: str
        - `resource_id_or_fullname`: str
        - `resource_type`: str
        - `headers`: dict
        - `master_key`: st

    :Returns:
        dict

    """
    key = master_key.decode('base64')

    # Skipping lower casing of resource_id_or_fullname since it may now contain "ID" of the resource as part of the fullname
    text = '{verb}\n{resource_type}\n{resource_id_or_fullname}\n{x_date}\n{http_date}\n'.format(
        verb=(verb.lower() or ''),
        resource_type=(resource_type.lower() or ''),
        resource_id_or_fullname=(resource_id_or_fullname or ''),
        x_date=headers.get(http_constants.HttpHeaders.XDate, '').lower(),
        http_date=headers.get(http_constants.HttpHeaders.HttpDate, '').lower())
   
    body = text.decode('utf8')

    hm = hmac.new(key, body, sha256)
    signature = hm.digest().encode('base64')

    master_token = 'master'
    token_version = '1.0'
    return 'type={type}&ver={ver}&sig={sig}'.format(type=master_token,
                                                    ver=token_version,
                                                    sig=signature[:-1])


def __GetAuthorizationTokenUsingResourceTokens(resource_tokens,
                                              path,
                                              resource_id_or_fullname):
    """Get the authorization token using `resource_tokens`.

    :Parameters:
        - `resource_tokens`: dict
        - `path`: str
        - `resource_id_or_fullname`: str

    :Returns:
        dict

    """
    if resource_tokens.get(resource_id_or_fullname):
        return resource_tokens[resource_id_or_fullname]
    else:
        path_parts = path.split('/')
        resource_types = ['dbs', 'colls', 'docs', 'sprocs', 'udfs', 'triggers',
                          'users', 'permissions', 'attachments', 'media',
                          'conflicts', 'offers']
        for one_part in reversed(path_parts):
            if not one_part in resource_types and one_part in resource_tokens:
                return resource_tokens[one_part]
        return None