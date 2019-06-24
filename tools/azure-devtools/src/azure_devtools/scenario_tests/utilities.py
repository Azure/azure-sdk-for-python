# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import math
import os
import base64
import inspect


def create_random_name(prefix='aztest', length=24):
    if len(prefix) > length:
        raise ValueError('The length of the prefix must not be longer than random name length')

    padding_size = length - len(prefix)
    if padding_size < 4:
        raise ValueError('The randomized part of the name is shorter than 4, which may not be able to offer enough '
                         'randomness')

    random_bytes = os.urandom(int(math.ceil(float(padding_size) / 8) * 5))
    random_padding = base64.b32encode(random_bytes)[:padding_size]

    return str(prefix + random_padding.decode().lower())


def get_sha1_hash(file_path):
    sha1 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


def _get_content_type(entity):
    # 'headers' is a field of 'request', but it is a dict-key in 'response'
    headers = getattr(entity, 'headers', None)
    if headers is None:
        headers = entity.get('headers')

    content_type = None
    if headers:
        content_type = headers.get('content-type', None)
        if content_type:
            # content-type could an array from response, let us extract it out
            content_type = content_type[0] if isinstance(content_type, list) else content_type
            content_type = content_type.split(";")[0].lower()
    return content_type


def is_text_payload(entity):
    text_content_list = ['application/json', 'application/xml', 'text/', 'application/test-content']

    content_type = _get_content_type(entity)
    if content_type:
        return any(content_type.startswith(x) for x in text_content_list)
    return True


def is_json_payload(entity):
    return _get_content_type(entity) == 'application/json'


def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not is_preparer_func(fn):
        args, _, kw, _ = inspect.getargspec(fn)  # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]


def is_preparer_func(fn):
    return getattr(fn, '__is_preparer', False)
