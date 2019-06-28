# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class HTTPError(Exception):
    '''
    Represents an HTTP Exception when response status code >= 300.

    :ivar int status:
        the status code of the response
    :ivar str message:
        the message
    :ivar list headers:
        the returned headers, as a list of (name, value) pairs
    :ivar bytes body:
        the body of the response
    '''

    def __init__(self, status, message, respheader, respbody):
        self.status = status
        self.respheader = respheader
        self.respbody = respbody
        Exception.__init__(self, message)


class HTTPResponse(object):
    '''
    Represents a response from an HTTP request.
    
    :ivar int status:
        the status code of the response
    :ivar str message:
        the message
    :ivar dict headers:
        the returned headers
    :ivar bytes body:
        the body of the response
    '''

    def __init__(self, status, message, headers, body):
        self.status = status
        self.message = message
        self.headers = headers
        self.body = body


class HTTPRequest(object):
    '''
    Represents an HTTP Request.

    :ivar str host:
        the host name to connect to
    :ivar str method:
        the method to use to connect (string such as GET, POST, PUT, etc.)
    :ivar str path:
        the uri fragment
    :ivar dict query:
        query parameters
    :ivar dict headers:
        header values
    :ivar bytes body:
        the body of the request.
    '''

    def __init__(self):
        self.host = ''
        self.method = ''
        self.path = ''
        self.query = {}  # list of (name, value)
        self.headers = {}  # list of (header name, header value)
        self.body = ''
