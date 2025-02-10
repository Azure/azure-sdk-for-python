"""
Functions related to masking Websocket frames.
https://tools.ietf.org/html/rfc6455#section-5.3

"""

import functools
from typing import List

@functools.lru_cache
def _xor_table() -> List[bytes]:
    return [bytes(a ^ b for a in range(256)) for b in range(256)]


def mask_payload(masking_key, data):
    """XOR mask bytes.

    `masking_key` should be bytes.
    `data` should be a bytearray, and is mutated.

    """
    _XOR_TABLE = _xor_table()
    a, b, c, d = (_XOR_TABLE[n] for n in bytearray(masking_key))
    data[::4] = data[::4].translate(a)
    data[1::4] = data[1::4].translate(b)
    data[2::4] = data[2::4].translate(c)
    data[3::4] = data[3::4].translate(d)
