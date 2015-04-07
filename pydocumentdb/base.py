# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Base functions.
"""

import base64
import datetime
import urllib
import uuid

import pydocumentdb.auth as auth
import pydocumentdb.http_constants as http_constants
import pydocumentdb.runtime_constants as runtime_constants


def GetHeaders(document_client,
               default_headers,
               verb,
               path,
               resource_id,
               resource_type,
               options):
    """Gets HTTP request headers.

    :Parameters:
        - `document_client`: document_client.DocumentClient
        - `default_headers`: dict
        - `verb`: str
        - `path`: str
        - `resource_id`: str
        - `resource_type`: str
        - `options`: dict

    :Returns:
        dict, the HTTP request headers.

    """
    headers = dict(default_headers)
    options = options or {}

    if options.get('continuation'):
        headers[http_constants.HttpHeaders.Continuation] = (
            options['continuation'])

    pre_trigger_include = options.get('preTriggerInclude')
    if pre_trigger_include:
        headers[http_constants.HttpHeaders.PreTriggerInclude] = (
            pre_trigger_include
            if isinstance(pre_trigger_include, str)
            else (',').join(pre_trigger_include))

    post_trigger_include = options.get('postTriggerInclude')
    if post_trigger_include:
        headers[http_constants.HttpHeaders.PostTriggerInclude] = (
            post_trigger_include
            if isinstance(post_trigger_include, str)
            else (',').join(post_trigger_include))

    if options.get('maxItemCount'):
        headers[http_constants.HttpHeaders.PageSize] = options['maxItemCount']

    access_condition = options.get('accessCondition')
    if access_condition:
        if access_condition['type'] == 'IfMatch':
            headers[http_constants.HttpHeaders.IfMatch] = access_condition['condition']
        else:
            headers[http_constants.HttpHeaders.IfNoneMatch] = access_condition['condition']

    if options.get('indexingDirective'):
        headers[http_constants.HttpHeaders.IndexingDirective] = (
            options['indexingDirective'])

    # TODO: add consistency level validation.
    if options.get('consistencyLevel'):
        headers[http_constants.HttpHeaders.ConsistencyLevel] = (
            options['consistencyLevel'])

    # TODO: add session token automatic handling in case of session consistency.
    if options.get('sessionToken'):
        headers[http_constants.HttpHeaders.SessionToken] = (
            options['sessionToken'])

    if options.get('enableScanInQuery'):
        headers[http_constants.HttpHeaders.EnableScanInQuery] = (
            options['enableScanInQuery'])

    if options.get('resourceTokenExpirySeconds'):
        headers[http_constants.HttpHeaders.ResourceTokenExpiry] = (
            options['resourceTokenExpirySeconds'])

    if options.get('offerType'):
        headers[http_constants.HttpHeaders.OfferType] = options['offerType']

    if document_client.master_key:
        headers[http_constants.HttpHeaders.XDate] = (
            datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))

    if document_client.master_key or document_client.resource_tokens:
        # -_.!~*'() are valid characters in url, and shouldn't be quoted.
        headers[http_constants.HttpHeaders.Authorization] = urllib.quote(
            auth.GetAuthorizationHeader(document_client,
                                        verb,
                                        path,
                                        resource_id,
                                        resource_type,
                                        headers),
            '-_.!~*\'()')

    if verb == 'post' or verb == 'put':
        if not headers.get(http_constants.HttpHeaders.ContentType):
            headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.Json

    if not headers.get(http_constants.HttpHeaders.Accept):
        headers[http_constants.HttpHeaders.Accept] = runtime_constants.MediaTypes.Json

    return headers


def GetIdFromLink(resource_link):
    """Gets resource id from resource link.

    :Parameters:
        - `resource_link`: str

    :Returns:
        str, the resource ID from the resource link.

    """
    if resource_link[-1] != '/':
        resource_link = resource_link + '/'

    if resource_link[0] != '/':
        resource_link = '/' + resource_link

    # The path will be in the form of 
    # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/ or
    # /[resourceType]/[resourceId]/ .... /[resourceType]/
    # The result of split will be in the form of
    # [[[resourceType], [resourceId] ... ,[resourceType], [resourceId], ""]
    # In the first case, to extract the resourceId it will the element
    # before last ( at length -2 ) and the the type will before it
    # ( at length -3 )
    # In the second case, to extract the resource type it will the element
    # before last ( at length -2 )
    path_parts = resource_link.split("/")
    if len(path_parts) % 2 == 0:
        # request in form
        # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/.
        return path_parts[-2]
    return None


def GetAttachmentIdFromMediaId(media_id):
    """Gets attachment id from media id.

    :Parameters:
        - `media_id`: str

    :Returns:
        str, the attachment id from the media id.

    """
    altchars = '+-'
    # altchars for '+' and '/'. We keep '+' but replace '/' with '-'
    buffer = base64.b64decode(str(media_id), altchars)
    resoure_id_length = 20
    attachment_id = ''
    if len(buffer) > resoure_id_length:
        # We are cuting off the storage index.
        attachment_id = base64.b64encode(buffer[0:resoure_id_length], altchars)
    else:
        attachment_id = media_id

    return attachment_id


def GenerateGuidId():
    """Gets a random GUID.

    Note that here we use python's UUID generation library. Basically UUID
    is the same as GUID when represented as a string.

    :Returns:
        str, the generated random GUID.

    """
    return str(uuid.uuid4())