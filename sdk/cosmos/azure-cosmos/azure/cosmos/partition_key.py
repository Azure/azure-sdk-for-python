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

"""Create partition keys in the Azure Cosmos DB SQL API service.
"""


class NonePartitionKeyValue(object):
    """Represents None value for partitionKey when it's missing in a container.
    """


class _Empty(object):
    """Represents empty value for partitionKey when it's missing in an item belonging
    to a migrated container.
    """


class _Undefined(object):
    """Represents undefined value for partitionKey when it's missing in an item belonging
    to a multi-partition container.
    """


class PartitionKey(dict):
    """Key used to partition a container into logical partitions.

    See https://docs.microsoft.com/azure/cosmos-db/partitioning-overview#choose-partitionkey
    for information on how to choose partition keys.

    :ivar path: The path of the partition key
    :ivar kind: What kind of partition key is being defined (default: "Hash")
    :ivar version: The version of the partition key (default: 2)
    """

    def __init__(self, path, kind="Hash", version=2):  # pylint: disable=super-init-not-called
        # (str, str) -> None
        self.path = path
        self.kind = kind
        self.version = version

    def __repr__(self):
        # type () -> str
        return "<PartitionKey [{}]>".format(self.path)[:1024]

    @property
    def kind(self):
        return self["kind"]

    @kind.setter
    def kind(self, value):
        self["kind"] = value

    @property
    def path(self):
        # () -> str
        return self["paths"][0]

    @path.setter
    def path(self, value):
        # (str) -> None
        self["paths"] = [value]

    @property
    def version(self):
        return self["version"]

    @version.setter
    def version(self, value):
        self["version"] = value
