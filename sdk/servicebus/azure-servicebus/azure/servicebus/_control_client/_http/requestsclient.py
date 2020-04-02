# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# pylint: skip-file


class _Response(object):

    ''' Response class corresponding to the response returned from httplib
    HTTPConnection. '''

    def __init__(self, response):
        self.status = response.status_code
        self.reason = response.reason
        self.respbody = response.content
        self.length = len(response.content)
        self.headers = []
        for key, name in response.headers.items():
            self.headers.append((key.lower(), name))

    def getheaders(self):
        '''Returns response headers.'''
        return self.headers

    def read(self, _length=None):
        '''Returns response body. '''
        if _length:
            return self.respbody[:_length]
        return self.respbody


class _RequestsConnection(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self, host, protocol, session, timeout):
        self.host = host
        self.protocol = protocol
        self.session = session
        self.headers = {}
        self.method = None
        self.body = None
        self.response = None
        self.uri = None
        self.timeout = timeout

        # By default, requests adds an Accept:*/* to the session, which causes
        # issues with some Azure REST APIs. Removing it here gives us the flexibility
        # to add it back on a case by case basis via putheader.
        if 'Accept' in self.session.headers:
            del self.session.headers['Accept']

    def close(self):
        pass

    def set_tunnel(self, host, port=None, headers=None):
        self.session.proxies['http'] = 'http://{}:{}'.format(host, port)
        self.session.proxies['https'] = 'https://{}:{}'.format(host, port)
        if headers:
            self.session.headers.update(headers)

    def set_proxy_credentials(self, user, password):
        pass

    def putrequest(self, method, uri):
        self.method = method
        self.uri = self.protocol + '://' + self.host + uri

    def putheader(self, name, value):
        self.headers[name] = value

    def endheaders(self):
        pass

    def send(self, request_body):
        self.response = self.session.request(
            self.method, self.uri, data=request_body,
            headers=self.headers, timeout=self.timeout)

    def getresponse(self):
        return _Response(self.response)
