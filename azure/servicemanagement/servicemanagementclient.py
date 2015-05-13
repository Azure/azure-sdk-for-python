#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import os
import sys
import time

from azure import (
    WindowsAzureError,
    DEFAULT_HTTP_TIMEOUT,
    MANAGEMENT_HOST,
    WindowsAzureAsyncOperationError,
    _ERROR_ASYNC_OP_FAILURE,
    _ERROR_ASYNC_OP_TIMEOUT,
    _get_request_body,
    _str,
    _validate_not_none,
    _update_request_uri_query,
    )
from azure.http import (
    HTTPError,
    HTTPRequest,
    )
from azure.http.httpclient import _HTTPClient
from azure.servicemanagement import (
    AZURE_MANAGEMENT_CERTFILE,
    AZURE_MANAGEMENT_SUBSCRIPTIONID,
    Operation,
    _MinidomXmlToObject,
    _management_error_handler,
    parse_response_for_async_op,
    X_MS_VERSION,
    )


class _ServiceManagementClient(object):

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST, request_session=None,
                 timeout=DEFAULT_HTTP_TIMEOUT):
        self.requestid = None
        self.subscription_id = subscription_id
        self.cert_file = cert_file
        self.host = host
        self.request_session = request_session
        self.x_ms_version = X_MS_VERSION
        self.content_type = 'application/atom+xml;type=entry;charset=utf-8'

        if not self.cert_file and not request_session:
            if AZURE_MANAGEMENT_CERTFILE in os.environ:
                self.cert_file = os.environ[AZURE_MANAGEMENT_CERTFILE]

        if not self.subscription_id:
            if AZURE_MANAGEMENT_SUBSCRIPTIONID in os.environ:
                self.subscription_id = os.environ[
                    AZURE_MANAGEMENT_SUBSCRIPTIONID]

        if not self.request_session:
            if not self.cert_file or not self.subscription_id:
                raise WindowsAzureError(
                    'You need to provide subscription id and certificate file')

        self._httpclient = _HTTPClient(
            service_instance=self, cert_file=self.cert_file,
            request_session=self.request_session, timeout=timeout)
        self._filter = self._httpclient.perform_request

    def with_filter(self, filter):
        '''Returns a new service which will process requests with the
        specified filter.  Filtering operations can include logging, automatic
        retrying, etc...  The filter is a lambda which receives the HTTPRequest
        and another lambda.  The filter can perform any pre-processing on the
        request, pass it off to the next lambda, and then perform any
        post-processing on the response.'''
        res = type(self)(self.subscription_id, self.cert_file, self.host,
                         self.request_session, self._httpclient.timeout)
        old_filter = self._filter

        def new_filter(request):
            return filter(request, old_filter)

        res._filter = new_filter
        return res

    def set_proxy(self, host, port, user=None, password=None):
        '''
        Sets the proxy server host and port for the HTTP CONNECT Tunnelling.

        host:
            Address of the proxy. Ex: '192.168.0.100'
        port:
            Port of the proxy. Ex: 6000
        user:
            User for proxy authorization.
        password:
            Password for proxy authorization.
        '''
        self._httpclient.set_proxy(host, port, user, password)

    @property
    def timeout(self):
        return self._httpclient.timeout

    @timeout.setter
    def timeout(self, value):
        self._httpclient.timeout = value

    def perform_get(self, path, x_ms_version=None):
        '''
        Performs a GET request and returns the response.

        path:
            Path to the resource.
            Ex: '/<subscription-id>/services/hostedservices/<service-name>'
        x_ms_version:
            If specified, this is used for the x-ms-version header.
            Otherwise, self.x_ms_version is used.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host = self.host
        request.path = path
        request.path, request.query = _update_request_uri_query(request)
        request.headers = self._update_management_header(request, x_ms_version)
        response = self._perform_request(request)

        return response

    def perform_put(self, path, body, x_ms_version=None):
        '''
        Performs a PUT request and returns the response.

        path:
            Path to the resource.
            Ex: '/<subscription-id>/services/hostedservices/<service-name>'
        body:
            Body for the PUT request.
        x_ms_version:
            If specified, this is used for the x-ms-version header.
            Otherwise, self.x_ms_version is used.
        '''
        request = HTTPRequest()
        request.method = 'PUT'
        request.host = self.host
        request.path = path
        request.body = _get_request_body(body)
        request.path, request.query = _update_request_uri_query(request)
        request.headers = self._update_management_header(request, x_ms_version)
        response = self._perform_request(request)

        return response

    def perform_post(self, path, body, x_ms_version=None):
        '''
        Performs a POST request and returns the response.

        path:
            Path to the resource.
            Ex: '/<subscription-id>/services/hostedservices/<service-name>'
        body:
            Body for the POST request.
        x_ms_version:
            If specified, this is used for the x-ms-version header.
            Otherwise, self.x_ms_version is used.
        '''

        request = HTTPRequest()
        request.method = 'POST'
        request.host = self.host
        request.path = path
        request.body = _get_request_body(body)
        request.path, request.query = _update_request_uri_query(request)
        request.headers = self._update_management_header(request, x_ms_version)
        response = self._perform_request(request)

        return response

    def perform_delete(self, path, x_ms_version=None):
        '''
        Performs a DELETE request and returns the response.

        path:
            Path to the resource.
            Ex: '/<subscription-id>/services/hostedservices/<service-name>'
        x_ms_version:
            If specified, this is used for the x-ms-version header.
            Otherwise, self.x_ms_version is used.
        '''
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = self.host
        request.path = path
        request.path, request.query = _update_request_uri_query(request)
        request.headers = self._update_management_header(request, x_ms_version)
        response = self._perform_request(request)

        return response

    #--Operations for tracking asynchronous requests ---------------------
    def wait_for_operation_status_progress_default_callback(elapsed):
        sys.stdout.write('.')
        sys.stdout.flush()

    def wait_for_operation_status_success_default_callback(elapsed):
        sys.stdout.write('\n')
        sys.stdout.flush()

    def wait_for_operation_status_failure_default_callback(elapsed, ex):
        sys.stdout.write('\n')
        sys.stdout.flush()
        print(vars(ex.result))
        raise ex

    def wait_for_operation_status(self,
        request_id, wait_for_status='Succeeded', timeout=30, sleep_interval=5,
        progress_callback=wait_for_operation_status_progress_default_callback,
        success_callback=wait_for_operation_status_success_default_callback,
        failure_callback=wait_for_operation_status_failure_default_callback):
        '''
        Waits for an asynchronous operation to complete.

        This calls get_operation_status in a loop and returns when the expected
        status is reached. The result of get_operation_status is returned. By
        default, an exception is raised on timeout or error status.

        request_id:
            The request ID for the request you wish to track.
        wait_for_status:
            Status to wait for. Default is 'Succeeded'.
        timeout:
            Total timeout in seconds. Default is 30s.
        sleep_interval:
            Sleep time in seconds for each iteration. Default is 5s.
        progress_callback:
            Callback for each iteration.
            Default prints '.'.
            Set it to None for no progress notification.
        success_callback:
            Callback on success. Default prints newline.
            Set it to None for no success notification.
        failure_callback:
            Callback on failure. Default prints newline+error details then
            raises exception.
            Set it to None for no failure notification.
        '''
        loops = timeout // sleep_interval + 1
        start_time = time.time()
        for _ in range(loops):
            result = self.get_operation_status(request_id)
            elapsed = time.time() - start_time
            if result.status == wait_for_status:
                if success_callback is not None:
                    success_callback(elapsed)
                return result
            elif result.error:
                if failure_callback is not None:
                    ex = WindowsAzureAsyncOperationError(_ERROR_ASYNC_OP_FAILURE, result)
                    failure_callback(elapsed, ex)
                return result
            else:
                if progress_callback is not None:
                    progress_callback(elapsed)
                time.sleep(sleep_interval)

        if failure_callback is not None:
            ex = WindowsAzureAsyncOperationError(_ERROR_ASYNC_OP_TIMEOUT, result)
            failure_callback(elapsed, ex)
        return result

    def get_operation_status(self, request_id):
        '''
        Returns the status of the specified operation. After calling an
        asynchronous operation, you can call Get Operation Status to determine
        whether the operation has succeeded, failed, or is still in progress.

        request_id:
            The request ID for the request you wish to track.
        '''
        _validate_not_none('request_id', request_id)
        return self._perform_get(
            '/' + self.subscription_id + '/operations/' + _str(request_id),
            Operation)

    #--Helper functions --------------------------------------------------
    def _perform_request(self, request):
        try:
            resp = self._filter(request)
        except HTTPError as ex:
            return _management_error_handler(ex)

        return resp

    def _update_management_header(self, request, x_ms_version):
        ''' Add additional headers for management. '''

        if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
            request.headers.append(('Content-Length', str(len(request.body))))

        # append additional headers base on the service
        request.headers.append(('x-ms-version', x_ms_version or self.x_ms_version))

        # if it is not GET or HEAD request, must set content-type.
        if not request.method in ['GET', 'HEAD']:
            for name, _ in request.headers:
                if 'content-type' == name.lower():
                    break
            else:
                request.headers.append(
                    ('Content-Type',
                     self.content_type))

        return request.headers

    def _perform_get(self, path, response_type=None, x_ms_version=None):
        response = self.perform_get(path, x_ms_version)

        if response_type is not None:
            return _MinidomXmlToObject.parse_response(response, response_type)

        return response

    def _perform_put(self, path, body, async=False, x_ms_version=None):
        response = self.perform_put(path, body, x_ms_version)

        if async:
            return parse_response_for_async_op(response)

        return None

    def _perform_post(self, path, body, response_type=None, async=False,
                      x_ms_version=None):
        response = self.perform_post(path, body, x_ms_version)

        if response_type is not None:
            return _MinidomXmlToObject.parse_response(response, response_type)

        if async:
            return parse_response_for_async_op(response)

        return None

    def _perform_delete(self, path, async=False, x_ms_version=None):
        response = self.perform_delete(path, x_ms_version)

        if async:
            return parse_response_for_async_op(response)

        return None

    def _get_path(self, resource, name):
        path = '/' + self.subscription_id + '/' + resource
        if name is not None:
            path += '/' + _str(name)
        return path

    def _get_cloud_services_path(self, cloud_service_id, resource=None, name=None):
        path = '/' + self.subscription_id + '/cloudservices/' + cloud_service_id
        if resource is not None:
            path += '/resources/' + _str(resource)
        if name is not None:
            path += '/' + _str(name)
        return path
