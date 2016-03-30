# Copyright (c) Microsoft Corporation.  All rights reserved.

"""Base functions.
"""

import base64
import datetime
import json
import urllib
import uuid

import pydocumentdb.auth as auth
import pydocumentdb.documents as documents
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

    if options.get('offerThroughput'):
        headers[http_constants.HttpHeaders.OfferThroughput] = options['offerThroughput']

    if 'partitionKey' in options:
        # if partitionKey value is Undefined, serailize it as {} to be consistent with other SDKs
        if options.get('partitionKey') is documents.Undefined:
            headers[http_constants.HttpHeaders.PartitionKey] = [{}]
        # else serialize using json dumps method which apart from regular values will serialize None into null
        else:
            headers[http_constants.HttpHeaders.PartitionKey] = json.dumps([options['partitionKey']])

    if options.get('enableCrossPartitionQuery'):
        headers[http_constants.HttpHeaders.EnableCrossPartitionQuery] = options['enableCrossPartitionQuery']

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


def GetResourceIdOrFullNameFromLink(resource_link):
    """Gets resource id or full name from resource link.

    :Parameters:
        - `resource_link`: str

    :Returns:
        str, the resource id or full name from the resource link.

    """
    # For named based, the resource link is the full name
    if IsNameBased(resource_link):
        return resource_link
    
    # Padding the resource link with leading and trailing slashes if not already
    if resource_link[-1] != '/':
        resource_link = resource_link + '/'

    if resource_link[0] != '/':
        resource_link = '/' + resource_link

    # The path will be in the form of 
    # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/ or
    # /[resourceType]/[resourceId]/ .... /[resourceType]/
    # The result of split will be in the form of
    # ["", [resourceType], [resourceId] ... ,[resourceType], [resourceId], ""]
    # In the first case, to extract the resourceId it will the element
    # before last ( at length -2 ) and the the type will before it
    # ( at length -3 )
    # In the second case, to extract the resource type it will the element
    # before last ( at length -2 )
    path_parts = resource_link.split("/")
    if len(path_parts) % 2 == 0:
        # request in form
        # /[resourceType]/[resourceId]/ .... /[resourceType]/[resourceId]/.
        # Lower casing of ResourceID, to be used in AuthorizationToken generation logic, where rest of the fields are lower cased
        # It's not being done there since the field might contain the "ID" in case of named based, which shouldn't be cased and used as is
        return str(path_parts[-2]).lower()
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

def GetPathFromLink(resource_link, resource_type=''):
    """Gets path from resource link with optional resource type

    :Parameters:
        - `resource_link`: str
        - `resource_type`: str

    :Returns:
        str, path from resource link with resource type appended(if provided).

    """
    resource_link = TrimBeginningAndEndingSlashes(resource_link)
        
    if IsNameBased(resource_link):
        # Replace special characters in string using the %xx escape. For example, space(' ') would be replaced by %20
        # This function is intended for quoting the path section of the URL and excludes '/' to be quoted as that's the default safe char
        resource_link = urllib.quote(resource_link)
        
    # Padding leading and trailing slashes to the path returned both for name based and resource id based links
    if resource_type:
        return '/' + resource_link + '/' + resource_type + '/'
    else:
        return '/' + resource_link + '/'
    
def IsNameBased(link):
    """Finds whether the link is name based or not

    :Parameters:
        - `link`: str

    :Returns:
        boolean, True if link is name based otherwise False.

    """
    if not link:
        return False

    # trimming the leading "/"
    if link.startswith('/') and len(link) > 1:
        link = link[1:]

    # Splitting the link(separated by "/") into parts 
    parts = link.split('/')

    # First part should be "dbs" 
    if len(parts) == 0 or not parts[0] or not parts[0].lower() == 'dbs':
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if len(parts) < 2 or not parts[1]:
    	return False

    # Either ResourceID or database name
    databaseID = parts[1];
    	
    # Length of databaseID(in case of ResourceID) is always 8
    if len(databaseID) != 8:
        	return True

    # Decoding the databaseID
    buffer = DecodeBase64String(str(databaseID))
    
    # Length of decoded buffer(in case of ResourceID) is always 4
    if len(buffer) != 4:
      	return True

    return False;

def IsDatabaseLink(link):
    """Finds whether the link is a database Self Link or a database ID based link

    :Parameters:
        - `link`: str, link to analyze

    :Returns:
        boolean, True or False.

    """
    if not link:
        return False

    # trimming the leading and trailing "/" from the input string
    link = TrimBeginningAndEndingSlashes(link)

    # Splitting the link(separated by "/") into parts 
    parts = link.split('/')

    if len(parts) != 2:
    	return False

    # First part should be "dbs" 
    if not parts[0] or not parts[0].lower() == 'dbs':
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if not parts[1]:
    	return False

    return True;

def IsDocumentCollectionLink(link):
    """Finds whether the link is a document colllection Self Link or a document colllection ID based link

    :Parameters:
        - `link`: str, link to analyze

    :Returns:
        boolean, True or False.

    """
    if not link:
        return False

    # trimming the leading and trailing "/" from the input string
    link = TrimBeginningAndEndingSlashes(link)

    # Splitting the link(separated by "/") into parts 
    parts = link.split('/')

    if len(parts) != 4:
    	return False

    # First part should be "dbs" 
    if not parts[0] or not parts[0].lower() == 'dbs':
        return False

    # Third part should be "colls" 
    if not parts[2] or not parts[2].lower() == 'colls':
        return False

    # The second part is the database id(ResourceID or Name) and cannot be empty
    if not parts[1]:
    	return False

    # The fourth part is the document collection id(ResourceID or Name) and cannot be empty
    if not parts[3]:
    	return False

    return True;

def GetDocumentCollectionLink(link):
    """Gets the document collection link

    :Parameters:
        - `link`: str, resource link

    :Returns:
        str, document collection link

    """
    link = TrimBeginningAndEndingSlashes(link)
    
    index = IndexOfNth(link, '/', 4)
    
    if index != -1:
        return link[0:index]
    else:
        raise ValueError('Unable to parse document collection link from ' + link)

def IndexOfNth(str, value, n):
    """Gets the index of Nth occurance of a given character in a string

    :Parameters:
        - `str`: str, input string
        - `value`: char, input char to be searched
        - `n`: int, Nth occurance of char to be searched

    :Returns:
        int, index of the Nth occurance in the string

    """
    remaining = n
    for i in range(0, len(str)):
        if str[i] == value:
            remaining -= 1
            if remaining == 0:
                return i
    return -1

def DecodeBase64String(string_to_decode):
    """Decodes a Base64 encoded string by replacing '-' with '/' 

    :Parameters:
        - `string_to_decode`: string to decode

    :Returns:
        str, path with beginning and ending slashes trimmed

    """
    # '-' is not supported char for decoding in Python(same as C# and Java) which has similar logic while parsing ResourceID generated by backend
    return base64.standard_b64decode(string_to_decode.replace('-', '/'))


def TrimBeginningAndEndingSlashes(path):
    """Trims beginning and ending slashes

    :Parameters:
        - `path`: str

    :Returns:
        str, path with beginning and ending slashes trimmed

    """
    if path.startswith('/'):
        # Returns substring starting from index 1 to end of the string
        path = path[1:]

    if path.endswith('/'):
        # Returns substring starting from beginning to last but one char in the string
        path = path[:-1]

    return path
    