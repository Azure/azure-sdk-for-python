# Copyright 2017, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

COMMON_ATTRIBUTES = {
    'AGENT': 'g.co/agent',
    'COMPONENT': 'component',
    'ERROR_MESSAGE': 'error.message',
    'ERROR_NAME': 'error.name',
    'HTTP_CLIENT_CITY': 'http.client_city',
    'HTTP_CLIENT_COUNTRY': 'http.client_country',
    'HTTP_CLIENT_PROTOCOL': 'http.client_protocol',
    'HTTP_CLIENT_REGION': 'http.client_region',
    'HTTP_HOST': 'http.host',
    'HTTP_METHOD': 'http.method',
    'HTTP_PATH': 'http.path',
    'HTTP_ROUTE': 'http.route',
    'HTTP_REDIRECTED_URL': 'http.redirected_url',
    'HTTP_REQUEST_SIZE': 'http.request_size',
    'HTTP_RESPONSE_SIZE': 'http.response_size',
    'HTTP_STATUS_CODE': 'http.status_code',
    'HTTP_URL': 'http.url',
    'HTTP_USER_AGENT': 'http.user_agent',
    'PID': 'pid',
    'STACKTRACE': 'stacktrace',
    'TID': 'tid',
}


GRPC_ATTRIBUTES = {
    'GRPC_HOST_PORT': 'grpc.host_port',
    'GRPC_METHOD': 'grpc.method',
}
