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

"""Internal class for client side partition implementation in the Azure Cosmos
database service.
"""

class Partition(object):
    """A class that holds the hash value and node name for a partition.
    """

    def __init__(self, hash_value=None, node=None):
        self.hash_value = hash_value
        self.node = node

    def GetNode(self):
        """Gets the name of the node(collection) for this object.
        """
        return self.node

    def __eq__(self, other):
        return (self.hash_value == other.hash_value) and (self.node == other.node)

    def __lt__(self, other):
        if self == other:
            return False

        return self.CompareTo(other.hash_value) < 0

    def CompareTo(self, other_hash_value):
        """Compare the passed hash value with the hash value of this object.
        """
        if len(self.hash_value) != len(other_hash_value):
            raise ValueError("Length of hashes doesn't match.")

        # The hash byte array that is returned from ComputeHash method has the MSB at the end of the array
        # so comparing the bytes from the end for compare operations.
        for i in range(0, len(self.hash_value)):
            if self.hash_value[len(self.hash_value) - i - 1] < other_hash_value[len(self.hash_value) - i - 1]:
                return -1
            if self.hash_value[len(self.hash_value) - i - 1] > other_hash_value[len(self.hash_value) - i - 1]:
                return 1
        return 0
