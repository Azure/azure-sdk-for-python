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
import unittest
import pytest
import struct

pytestmark = pytest.mark.cosmosEmulator
from azure.cosmos._cosmos_murmurhash3 import murmurhash3_128
from azure.cosmos._cosmos_integers import UInt128

@pytest.mark.usefixtures("teardown")
class MurmurHash3Test(unittest.TestCase):
    """Python Murmurhash3 Tests and its compatibility with backend implementation..
        """
    string_low_value = 2792699143512860960
    string_high_value = 15069672278200047189
    test_seed = UInt128.create(0, 0)
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
