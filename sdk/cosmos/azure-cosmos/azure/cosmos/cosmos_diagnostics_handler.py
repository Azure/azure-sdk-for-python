# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from multidict import CIMultiDict


class CosmosDiagnosticsHandler(CIMultiDict):
    # To customize the diagnostic handler, you can modify the conditions in the _preset_keys dictionary.
    # For example, to log if the duration is greater than 500 ms, you can set:
    # self._preset_keys['duration'] = lambda x: x > 500
    # Similarly, you can add or modify conditions for other keys as needed.
    def __init__(self) -> None:
        """
        A Preview Feature That is subject to significant changes.
        Initializes the CosmosDiagnosticsHandler with preset keys and their corresponding conditions.
        To customize the diagnostic handler, you can modify the conditions in the _preset_keys dictionary.
        For example, to log if the duration is greater than 500 ms, you can set:
        self._preset_keys['duration'] = lambda x: x > 500
        or
        def check_duration(duration: int) -> bool:
            return duration > 500
        self._preset_keys['duration'] = check_duration
        Similarly, you can add or modify conditions for other keys as needed.
        When Using this as an instance, you can modify the values of the keys in the dictionary.
        Example:
            handler = CosmosDiagnosticsHandler()
            handler['duration'] = lambda x: x > 500
            or with a function.
            def check_duration(duration: int) -> bool:
                return duration > 500
            handler['duration'] = check_duration
        """
        super().__init__()
        self._preset_keys = {
            'duration': lambda x: x > 1000,  # Log if duration is greater than 1000 ms
            'status code': (lambda x: (
                    isinstance(x, (list, tuple)) and x[0] != 200 and (x[1] is None or x[1] != 0)
            ) if isinstance(x, (list, tuple)) else x != 200),  # Log if status code is not 200
            'verb': None,  # No condition for verb
            'http version': None,  # No condition for http_version
            'database name': None,  # No condition for database_name
            'collection name': None,  # No condition for collection_name
            'resource type': None  # No condition for resource_type
        }
        for key, value in self._preset_keys.items():
            self[key] = value

    def __setitem__(self, key, value):
        if key.lower() in self._preset_keys:
            super().__setitem__(key, value)
        else:
            raise KeyError(f"Cannot add new key: {key}")

    def __delitem__(self, key):
        raise KeyError(f"Cannot delete key: {key}")

    def __call__(self, **kwargs) -> bool:
        status_code = kwargs.get('status_code')
        params = {
            'duration': kwargs.get('duration'),
            'status code': (status_code, kwargs.get('sub_status_code')) if status_code else None,
            'verb': kwargs.get('verb'),
            'http version': kwargs.get('http_version'),
            'database name': kwargs.get('database_name'),
            'collection name': kwargs.get('collection_name'),
            'resource type': kwargs.get('resource_type')
        }
        for key, param in params.items():
            if param is not None and self[key] is not None:
                if self[key](param):
                    return True
        return False

    def get_preset_keys(self):
        return self._preset_keys.keys()
