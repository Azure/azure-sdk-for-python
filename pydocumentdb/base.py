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


def Extend(obj, extent):
    """Extends `obj` with contents in `extent`.

    :Parameters:
        - `obj`: dict, the content to be extended
        - `extent`: dict, the content used to extend `obj`

    """
    for property in extent:
        if not hasattr(extent[property], '__call__'):
            # type is not 'function'.
            obj[property] = extent[property]
    return obj


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
    headers = Extend({}, default_headers)
    options = options or {}

    if 'continuation' in options and options['continuation']:
        headers[http_constants.HttpHeaders.Continuation] = (
            options['continuation'])

    if 'preTriggerInclude' in options and options['preTriggerInclude']:
        headers[http_constants.HttpHeaders.PreTriggerInclude] = (
            (',').join(options['preTriggerInclude'])
            if type(options['preTriggerInclude']) is list
            else options['preTriggerInclude'])

    if 'postTriggerInclude' in options and options['postTriggerInclude']:
        headers[http_constants.HttpHeaders.PostTriggerInclude] = (
            (',').join(options['postTriggerInclude'])
            if type(options['postTriggerInclude']) is list
            else options['postTriggerInclude'])

    if 'maxItemCount' in options and options['maxItemCount']:
        headers[http_constants.HttpHeaders.PageSize] = options['maxItemCount']

    if 'accessCondition'in options and options['accessCondition']:
        if options['accessCondition']['type'] == 'IfMatch':
            headers[http_constants.HttpHeaders.IfMatch] = (
                options['accessCondition']['condition'])
        else:
            headers[http_constants.HttpHeaders.IfNoneMatch] = (
                options['accessCondition']['condition'])

    if 'indexingDirective' in options and options['indexingDirective']:
        headers[http_constants.HttpHeaders.IndexingDirective] = (
            options['indexingDirective'])

    # TODO: add consistency level validation.
    if 'consistencyLevel' in options and options.consistency_level:
        headers[http_constants.HttpHeaders.ConsistencyLevel] = (
            options['consistencyLevel'])

    # TODO: add session token automatic handling in case of session consistency.
    if 'sessionToken' in options and options['sessionToken']:
        headers[http_constants.HttpHeaders.SessionToken] = (
            options['sessionToken'])

    if 'resourceTokenExpirySeconds' in options and options['resourceTokenExpirySeconds']:
        headers[http_constants.HttpHeaders.ResourceTokenExpiry] = (
            options['resourceTokenExpirySeconds'])

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
        if not http_constants.HttpHeaders.ContentType in headers:
            headers[http_constants.HttpHeaders.ContentType] = runtime_constants.MediaTypes.Json

    if not http_constants.HttpHeaders.Accept in headers:
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