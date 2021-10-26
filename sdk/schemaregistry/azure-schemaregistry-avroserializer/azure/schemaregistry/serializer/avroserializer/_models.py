# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

class MessageWithMetadata(object):
    """
    A message that contains binary data and a content type.

    :param bytes data: The message's binary data
    :param str content_type: The message's content type
    """
    def  __init__(self, **kwargs):
        self._data = kwargs.pop("data")
        self._content_type = kwargs.pop("content_type")

    @property
    def data(self):
        return self._data

    @property
    def content_type(self):
        return self._content_type

    @data.setter
    def data(self, data):
        self._data = data

    @content_type.setter
    def content_type(self, content_type):
        self._content_type = content_type

class ReadOnlyMessageWithMetadata(object):
    """
    A message that contains binary data and a content type.

    :param bytes data: The message's binary data
    :param str content_type: The message's content type
    """
    def  __init__(self, **kwargs):
        self._data = kwargs.pop("data")
        self._content_type = kwargs.pop("content_type")

    @property
    def data(self):
        return self._data

    @property
    def content_type(self):
        return self._content_type
