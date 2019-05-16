#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Internal class for Murmur hash implementation in the Azure Cosmos database service.
"""

from struct import pack, unpack
from six.moves import xrange

'''
pymmh3 was written by Fredrik Kihlander, and is placed in the public
domain. The author hereby disclaims copyright to this source code.

pure python implementation of the murmur3 hash algorithm

https://code.google.com/p/smhasher/wiki/MurmurHash3

This was written for the times when you do not want to compile c-code and install modules,
and you only want a drop-in murmur3 implementation.

As this is purely python it is FAR from performant and if performance is anything that is needed
a proper c-module is suggested!

This module is written to have the same format as mmh3 python package found here for simple conversions:

https://pypi.python.org/pypi/mmh3/2.0 
'''
class _MurmurHash(object):
    """ The 32 bit x86 version of MurmurHash3 implementation.
    """
    def ComputeHash(self, key):
        """
        Computes the hash of the value passed using MurmurHash3 algorithm.

        :param bytearray key:
            Byte array representing the key to be hashed.

        :return:
            32 bit hash value.
        :rtype: int
        """
        if key is None:
            raise ValueError("key is None.")

        hash_value = self._ComputeHash(key)
        return bytearray(pack('I', hash_value))

    @staticmethod
    def _ComputeHash( key, seed = 0x0 ):
        """Computes the hash of the value passed using MurmurHash3 algorithm with the seed value.
        """
        def fmix( h ):
            h ^= h >> 16
            h  = ( h * 0x85ebca6b ) & 0xFFFFFFFF
            h ^= h >> 13
            h  = ( h * 0xc2b2ae35 ) & 0xFFFFFFFF
            h ^= h >> 16
            return h

        length = len( key )
        nblocks = int( length / 4 )

        h1 = seed

        c1 = 0xcc9e2d51
        c2 = 0x1b873593

        # body
        for block_start in xrange( 0, nblocks * 4, 4 ):
            k1 = key[ block_start + 3 ] << 24 | \
                 key[ block_start + 2 ] << 16 | \
                 key[ block_start + 1 ] <<  8 | \
                 key[ block_start + 0 ]
             
            k1 = c1 * k1 & 0xFFFFFFFF
            k1 = ( k1 << 15 | k1 >> 17 ) & 0xFFFFFFFF # inlined ROTL32
            k1 = ( c2 * k1 ) & 0xFFFFFFFF
        
            h1 ^= k1
            h1  = ( h1 << 13 | h1 >> 19 ) & 0xFFFFFFFF # inlined _ROTL32 
            h1  = ( h1 * 5 + 0xe6546b64 ) & 0xFFFFFFFF

        # tail
        tail_index = nblocks * 4
        k1 = 0
        tail_size = length & 3

        if tail_size >= 3:
            k1 ^= key[ tail_index + 2 ] << 16
        if tail_size >= 2:
            k1 ^= key[ tail_index + 1 ] << 8
        if tail_size >= 1:
            k1 ^= key[ tail_index + 0 ]
    
        if tail_size != 0:
            k1  = ( k1 * c1 ) & 0xFFFFFFFF
            k1  = ( k1 << 15 | k1 >> 17 ) & 0xFFFFFFFF # _ROTL32
            k1  = ( k1 * c2 ) & 0xFFFFFFFF
            h1 ^= k1

        return fmix( h1 ^ length )






