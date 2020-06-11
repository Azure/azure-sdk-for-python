# Copyright 2018, OpenCensus Authors
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

# -*- coding: utf-8 -*-

import logging
import six

from google.protobuf.internal.encoder import _VarintBytes

from opencensus.tags import tag_map as tag_map_module

# Used for decoding hex bytes to hex string.
UTF8 = 'utf-8'

VERSION_ID = 0
TAG_FIELD_ID = 0
TAG_MAP_SERIALIZED_SIZE_LIMIT = 8192


class BinarySerializer(object):
    def from_byte_array(self, binary):
        if len(binary) <= 0:
            logging.warning("Input byte[] cannot be empty/")
            return tag_map_module.TagMap()
        else:
            buffer = memoryview(binary)
            version_id = buffer[0]
            if six.PY2:
                version_id = ord(version_id)
            if version_id != VERSION_ID:
                raise ValueError("Invalid version id.")
            return self._parse_tags(buffer)

    def to_byte_array(self, tag_context):
        encoded_bytes = b''
        encoded_bytes += _VarintBytes(VERSION_ID)
        total_chars = 0
        for tag in tag_context:
            tag_key, tag_value = tag
            total_chars += len(tag_key)
            total_chars += len(tag_value)
            encoded_bytes = self._encode_tag(
                tag_key, tag_value, encoded_bytes)
        if total_chars <= TAG_MAP_SERIALIZED_SIZE_LIMIT:
            return encoded_bytes
        else:  # pragma: NO COVER
            logging.warning("Size of the tag context exceeds the maximum size")

    def _parse_tags(self, buffer):
        tag_context = tag_map_module.TagMap()
        limit = len(buffer)
        total_chars = 0
        i = 1
        while i < limit:
            field_id = buffer[i] if six.PY3 else ord(buffer[i])
            if field_id == TAG_FIELD_ID:
                i += 1
                key = self._decode_string(buffer, i)
                i += len(key)
                total_chars += len(key)
                i += 1
                val = self._decode_string(buffer, i)
                i += len(val)
                total_chars += len(val)
                i += 1
                if total_chars > \
                        TAG_MAP_SERIALIZED_SIZE_LIMIT:  # pragma: NO COVER
                    logging.warning("Size of the tag context exceeds maximum")
                    break
                else:
                    tag_context.insert(str(key), str(val))
            else:
                break
        return tag_context

    def _encode_tag(self, tag_key, tag_value, encoded_bytes):
        encoded_bytes += _VarintBytes(TAG_FIELD_ID)
        encoded_bytes = self._encode_string(tag_key, encoded_bytes)
        encoded_bytes = self._encode_string(tag_value, encoded_bytes)
        return encoded_bytes

    def _encode_string(self, input_str, encoded_bytes):
        encoded_bytes += _VarintBytes(len(input_str))
        encoded_bytes += input_str.encode(UTF8)
        return encoded_bytes

    def _decode_string(self, buffer, pos):
        length = buffer[pos] if six.PY3 else ord(buffer[pos])
        builder = ""
        i = 1
        while i <= length:
            bytes_to_decode = buffer[pos + i] if six.PY3 \
                else ord(buffer[pos + i])
            builder += _VarintBytes(bytes_to_decode).decode()
            i += 1
        return builder
