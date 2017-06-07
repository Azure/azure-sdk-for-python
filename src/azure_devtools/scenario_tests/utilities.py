# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import hashlib
import math
import os
import base64


def create_random_name(prefix='aztest', length=24):
    if len(prefix) > length:
        raise 'The length of the prefix must not be longer than random name length'

    padding_size = length - len(prefix)
    if padding_size < 4:
        raise 'The randomized part of the name is shorter than 4, which may not be able to offer ' \
              'enough randomness'

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
