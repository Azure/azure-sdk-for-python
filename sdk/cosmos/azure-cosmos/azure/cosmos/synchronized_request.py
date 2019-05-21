#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Synchronized request in the Azure Cosmos database service.
"""

import json

from six.moves.urllib.parse import urlparse, urlencode
import six

import azure.cosmos.documents as documents
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import azure.cosmos.retry_utility as retry_utility

def _IsReadableStream(obj):
    """Checks whether obj is a file-like readable stream.

    :rtype:
        boolean

    """
    if (hasattr(obj, 'read') and callable(getattr(obj, 'read'))):
        return True
    return False


def _RequestBodyFromData(data):
    """Gets request body from data.

    When `data` is dict and list into unicode string; otherwise return `data`
    without making any change.

    :param (str, unicode, file-like stream object, dict, list or None) data:

    :rtype:
        str, unicode, file-like stream object, or None

    """
    if isinstance(data, six.string_types) or _IsReadableStream(data):
        return data
    elif isinstance(data, (dict, list, tuple)):
        
        json_dumped = json.dumps(data, separators=(',',':'))

        if six.PY2:
            return json_dumped.decode('utf-8')
        else:
            return json_dumped
    return None


def _Request(global_endpoint_manager, request, connection_policy, requests_session, path, request_options, request_body):
    """Makes one http request using the requests module.

    :param _GlobalEndpointManager global_endpoint_manager:
    :param dict request:
        contains the resourceType, operationType, endpointOverride,
        useWriteEndpoint, useAlternateWriteEndpoint information
    :param documents.ConnectionPolicy connection_policy:
    :param requests.Session requests_session:
        Session object in requests module
    :param str resource_url:
        The url for the resource
    :param dict request_options:
    :param str request_body:
        Unicode or None

    :return:
        tuple of (result, headers)
    :rtype:
        tuple of (dict, dict)

    """
    is_media = request_options['path'].find('media') > -1
    is_media_stream = is_media and connection_policy.MediaReadMode == documents.MediaReadMode.Streamed

    connection_timeout = (connection_policy.MediaRequestTimeout
                          if is_media
                          else connection_policy.RequestTimeout)

    # Every request tries to perform a refresh
    global_endpoint_manager.refresh_endpoint_list(None)

    if (request.endpoint_override):
        base_url = request.endpoint_override
    else:
        base_url = global_endpoint_manager.resolve_service_endpoint(request)

    if path:
        resource_url = base_url + path
    else:
        resource_url = base_url

    parse_result = urlparse(resource_url)

    # The requests library now expects header values to be strings only starting 2.11, 
    # and will raise an error on validation if they are not, so casting all header values to strings.
    request_options['headers'] = { header: str(value) for header, value in request_options['headers'].items() } 

    # We are disabling the SSL verification for local emulator(localhost/127.0.0.1) or if the user
    # has explicitly specified to disable SSL verification.
    is_ssl_enabled = (parse_result.hostname != 'localhost' and parse_result.hostname != '127.0.0.1' and not connection_policy.DisableSSLVerification)
    
    if connection_policy.SSLConfiguration:
        ca_certs = connection_policy.SSLConfiguration.SSLCaCerts
        cert_files = (connection_policy.SSLConfiguration.SSLCertFile, connection_policy.SSLConfiguration.SSLKeyFile)

        response = requests_session.request(request_options['method'], 
                                resource_url, 
                                data = request_body, 
                                headers = request_options['headers'],
                                timeout = connection_timeout / 1000.0,
                                stream = is_media_stream,
                                verify = ca_certs,
                                cert = cert_files)
    else:
        response = requests_session.request(request_options['method'], 
                                    resource_url, 
                                    data = request_body, 
                                    headers = request_options['headers'],
                                    timeout = connection_timeout / 1000.0,
                                    stream = is_media_stream,
                                    # If SSL is disabled, verify = false
                                    verify = is_ssl_enabled)

    headers = dict(response.headers)

    # In case of media stream response, return the response to the user and the user
    # will need to handle reading the response.
    if is_media_stream:
        return (response.raw, headers)

    data = response.content
    if not six.PY2:
        # python 3 compatible: convert data from byte to unicode string
        data = data.decode('utf-8')

    if response.status_code >= 400:
        raise errors.HTTPFailure(response.status_code, data, headers)

    result = None
    if is_media:
        result = data
    else:
        if len(data) > 0:
            try:
                result = json.loads(data)
            except:
                raise errors.JSONParseFailure(data)

    return (result, headers)

def SynchronizedRequest(client,
                        request,
                        global_endpoint_manager,
                        connection_policy,
                        requests_session,
                        method,
                        path,
                        request_data,
                        query_params,
                        headers):
    """Performs one synchronized http request according to the parameters.

    :param object client:
        Document client instance
    :param dict request:
    :param _GlobalEndpointManager global_endpoint_manager: 
    :param  documents.ConnectionPolicy connection_policy:
    :param requests.Session requests_session:
        Session object in requests module
    :param str method:
    :param str path:
    :param (str, unicode, file-like stream object, dict, list or None) request_data:
    :param dict query_params:
    :param dict headers:

    :return:
        tuple of (result, headers)
    :rtype:
        tuple of (dict dict)

    """
    request_body = None
    if request_data:
        request_body = _RequestBodyFromData(request_data)
        if not request_body:
           raise errors.UnexpectedDataType(
               'parameter data must be a JSON object, string or' +
               ' readable stream.')

    request_options = {}
    request_options['path'] = path
    request_options['method'] = method
    if query_params:
        request_options['path'] += '?' + urlencode(query_params)

    request_options['headers'] = headers
    if request_body and (type(request_body) is str or
                         type(request_body) is six.text_type):
        request_options['headers'][http_constants.HttpHeaders.ContentLength] = (
            len(request_body))
    elif request_body is None:
        request_options['headers'][http_constants.HttpHeaders.ContentLength] = 0

    # Pass _Request function with it's parameters to retry_utility's Execute method that wraps the call with retries
    return retry_utility._Execute(client, global_endpoint_manager, _Request, request, connection_policy, requests_session, path, request_options, request_body)

