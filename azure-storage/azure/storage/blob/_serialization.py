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
    BlobEnumResults,
    BlobResult,
    Blob,
    BlobPrefix,
    BlobBlock,
    BlobBlockList,
)


def _update_storage_blob_header(request, authentication):
    request = _update_storage_header(request)
    current_time = format_date_time(time())
    request.headers.append(('x-ms-date', current_time))
    request.headers.append(
        ('Content-Type', 'application/octet-stream Charset=UTF-8'))
    authentication.sign_request(request)

    return request.headers


def _parse_blob_enum_results_list(response):
    respbody = response.body
    return_obj = BlobEnumResults()
    enum_results = ETree.fromstring(respbody)

    for child in enum_results.findall('./Blobs/Blob'):
        return_obj.blobs.append(_ETreeXmlToObject.fill_instance_element(child, Blob))

    for child in enum_results.findall('./Blobs/BlobPrefix'):
        return_obj.prefixes.append(
            _ETreeXmlToObject.fill_instance_element(child, BlobPrefix))

    for name, value in vars(return_obj).items():
        if name == 'blobs' or name == 'prefixes':
            continue
        value = _ETreeXmlToObject.fill_data_member(enum_results, name, value)
        if value is not None:
            setattr(return_obj, name, value)

    return return_obj


def _convert_block_list_to_xml(block_id_list):
    '''
    Convert a block list to xml to send.

    block_id_list:
        a str list containing the block ids that are used in put_block_list.
    Only get block from latest blocks.
    '''
    if block_id_list is None:
        return ''
    xml = '<?xml version="1.0" encoding="utf-8"?><BlockList>'
    for value in block_id_list:
        xml += '<Latest>{0}</Latest>'.format(_encode_base64(value))

    return xml + '</BlockList>'


def _create_blob_result(response):
    blob_properties = _parse_response_for_dict(response)
    return BlobResult(response.body, blob_properties)


def _convert_block_etree_element_to_blob_block(block_element):
    block_id = _decode_base64_to_text(block_element.findtext('./Name', ''))
    block_size = int(block_element.findtext('./Size'))

    return BlobBlock(block_id, block_size)


def _convert_response_to_block_list(response):
    '''
    Converts xml response to block list class.
    '''
    block_list = BlobBlockList()

    list_element = ETree.fromstring(response.body)

    for block_element in list_element.findall('./CommittedBlocks/Block'):
        block = _convert_block_etree_element_to_blob_block(block_element)
        block_list.committed_blocks.append(block)

    for block_element in list_element.findall('./UncommittedBlocks/Block'):
        block = _convert_block_etree_element_to_blob_block(block_element)
        block_list.uncommitted_blocks.append(block)

    return block_list
