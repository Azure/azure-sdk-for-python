# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

_DEFAULT_LENGTH = 1024 * 1024
_BYTE_BUFFER = [_DEFAULT_LENGTH, os.urandom(_DEFAULT_LENGTH)]


def get_random_bytes(buffer_length):
    if buffer_length > _BYTE_BUFFER[0]:
        _BYTE_BUFFER[0] = buffer_length
        _BYTE_BUFFER[1] = os.urandom(buffer_length)
    return _BYTE_BUFFER[1][:buffer_length]


class RandomStream:
    def __init__(self, length, initial_buffer_length=_DEFAULT_LENGTH):
        self._base_data = get_random_bytes(initial_buffer_length)
        self._data_length = length
        self._base_buffer_length = initial_buffer_length
        self._position = 0
        self._remaining = length

    def reset(self):
        self._position = 0
        self._remaining = self._data_length

    def read(self, size=None):
        if self._remaining == 0:
            return b""

        if size is None:
            e = self._base_buffer_length
        else:
            e = size
        e = min(e, self._remaining)
        if e > self._base_buffer_length:
            self._base_data = get_random_bytes(e)
            self._base_buffer_length = e
        self._remaining = self._remaining - e
        self._position += e
        return self._base_data[:e]

    def tell(self):
        return self._position

    def seek(self, index, whence=0):
        if whence == 0:
            self._position = index
        elif whence == 1:
            self._position = self._position + index
        elif whence == 2:
            self._position = self._data_length - 1 + index

    def remaining(self):
        return self._remaining


class WriteStream:
    def __init__(self):
        self._position = 0

    def reset(self):
        self._position = 0

    def write(self, content):
        length = len(content)
        self._position += length
        return length

    def seek(self, index):
        self._position = index

    def seekable(self):
        return True

    def tell(self):
        return self._position
