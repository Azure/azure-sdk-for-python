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
from time import time
from wsgiref.handlers import format_date_time
from .._common_serialization import (
    _parse_response_for_dict,
    ETree,
    _ETreeXmlToObject,
)
from .._common_conversion import (
    _decode_base64_to_text,
    _encode_base64,
)
from .._serialization import _update_storage_header
from .models import (
    FileAndDirectoryEnumResults,
    FileResult,
    File,
    Directory
)


def _update_storage_file_header(request, authentication):
    request = _update_storage_header(request)
    current_time = format_date_time(time())
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(
        ('Content-Type', 'application/octet-stream Charset=UTF-8'))
    authentication.sign_request(request)

    return request.headers


def _parse_file_enum_results_list(response):
    respbody = response.body
    return_obj = FileAndDirectoryEnumResults()
    enum_results = ETree.fromstring(respbody)

    for child in enum_results.findall('./Entries/File'):
        return_obj.files.append(_ETreeXmlToObject.fill_instance_element(child, File))

    for child in enum_results.findall('./Entries/Directory'):
        return_obj.directories.append(
            _ETreeXmlToObject.fill_instance_element(child, Directory))

    for name, value in vars(return_obj).items():
        if name == 'files' or name == 'directories':
            continue
        value = _ETreeXmlToObject.fill_data_member(enum_results, name, value)
        if value is not None:
            setattr(return_obj, name, value)

    return return_obj


def _create_file_result(response):
    file_properties = _parse_response_for_dict(response)
    return FileResult(response.body, file_properties)
