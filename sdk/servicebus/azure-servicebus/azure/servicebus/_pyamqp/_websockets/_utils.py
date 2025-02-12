# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import List

@functools.lru_cache
def _xor_table() -> List[bytes]:
    return [bytes(a ^ b for a in range(256)) for b in range(256)]


def mask_payload(masking_key: bytes, data: bytearray) -> None:
    """XOR mask bytes.

    :param masking_key: The masking key.
    :type masking_key: bytes
    :param data: The data to mask.
    :type data: bytearray
    """
    _XOR_TABLE = _xor_table()
    a, b, c, d = (_XOR_TABLE[n] for n in bytearray(masking_key))
    data[::4] = data[::4].translate(a)
    data[1::4] = data[1::4].translate(b)
    data[2::4] = data[2::4].translate(c)
    data[3::4] = data[3::4].translate(d)