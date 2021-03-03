# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from io import BytesIO

from .random_stream import get_random_bytes, _DEFAULT_LENGTH


class AsyncRandomStream(BytesIO):
    def __init__(self, length, initial_buffer_length=_DEFAULT_LENGTH):
        super().__init__()
        self._base_data = get_random_bytes(initial_buffer_length)
        self._data_length = length
        self._base_buffer_length = initial_buffer_length
        self._position = 0
        self._remaining = length
        self._closed = False
    
    def reset(self):
        self._position = 0
        self._remaining = self._data_length
        self._closed = False

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

    def seek(self, index, whence=0):
        if whence == 0:
            self._position = index
        elif whence == 1:
            self._position = self._position + index
        elif whence == 2:
            self._position = self._data_length - 1 + index

    def tell(self):
        return self._position

    def remaining(self):
        return self._remaining

    def close(self):
        self._closed = True
