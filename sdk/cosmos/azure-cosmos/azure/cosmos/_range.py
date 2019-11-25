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

"""Range class implementation in the Azure Cosmos database service.
"""


class Range(object):
    """Represents the Range class used to map the partition key of the document
    to its associated collection.
    """

    def __init__(self, low, high):
        if low is None:
            raise ValueError("low is None.")
        if high is None:
            raise ValueError("high is None.")
        if low > high:
            raise ValueError("Range low value must be less than or equal the high value.")

        self.low = low
        self.high = high

    def __hash__(self):
        return hash((self.low, self.high))

    def __str__(self):
        return str(self.low) + str(self.high)

    def __eq__(self, other):
        return (self.low == other.low) and (self.high == other.high)

    def __lt__(self, other):
        if self == other:
            return False
        return self.low < other.low or self.high < other.high

    def Contains(self, other):
        """Check if the passed parameter is in the range of this object.
        """
        if other is None:
            raise ValueError("other is None.")

        if isinstance(other, Range):
            return other.low >= self.low and other.high <= self.high
        return self.Contains(Range(other, other))

    def Intersect(self, other):
        """Check if the passed parameter intersects the range of this object.
        """
        if isinstance(other, Range):
            max_low = self.low if (self.low >= other.low) else other.low
            min_high = self.high if (self.high <= other.high) else other.high

            if max_low <= min_high:
                return True

        return False
