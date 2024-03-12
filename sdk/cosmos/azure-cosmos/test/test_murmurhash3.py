# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import struct
import unittest

import pytest

from azure.cosmos._cosmos_integers import _UInt128
from azure.cosmos._cosmos_murmurhash3 import murmurhash3_128


@pytest.mark.cosmosEmulator
class TestMurmurHash3(unittest.TestCase):
    """Python Murmurhash3 Tests and its compatibility with backend implementation..
        """
    string_low_value = 2792699143512860960
    string_high_value = 15069672278200047189
    test_seed = _UInt128(0, 0)
    float_low_value = 16628891264555680919
    float_high_value = 12953474369317462

    def test_float_hash(self):
        ba = bytearray(struct.pack("d", 374.0))
        ret = murmurhash3_128(ba, self.test_seed)
        self.assertEqual(self.float_low_value, ret.get_low().value)
        self.assertEqual(self.float_high_value, ret.get_high().value)

    def test_string_hash(self):
        s = "afdgdd"  # cspell:disable-line
        ba = bytearray()
        ba.extend(s.encode('utf-8'))
        ret = murmurhash3_128(ba, self.test_seed)
        self.assertEqual(self.string_low_value, ret.get_low().value)
        self.assertEqual(self.string_high_value, ret.get_high().value)


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit as inst:
        if inst.args[0] is True:  # raised by sys.exit(True) when tests failed
            raise
