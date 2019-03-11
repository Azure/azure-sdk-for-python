"""
Create, read, update, and delete databases, containers, and items in Azure Cosmos DB SQL API databases.
"""

__all__ = ["ResponseMetadata", "User", "PartitionKey", "AccessCondition"]

from .query_iterator import QueryResultIterator
from .cosmos_client_connection import CosmosClientConnection
from .errors import HTTPFailure

from typing import (
    Any,
    Dict,
    Union
)

DatabaseId = Union["Database", Dict[str, Any], str]
ContainerId = Union["Container", Dict[str, Any], str]


class User:
    pass


class PartitionKey(dict):
    """ Key used to partition a container into logical partitions.

    See https://docs.microsoft.com/azure/cosmos-db/partitioning-overview#choose-partitionkey for more information
    on how to choose partition keys.

    :ivar path: The path of the partition key
    :ivar kind: What kind of partition key is being defined
    """

    def __init__(self, path, kind="Hash"):
        # (str, str) -> None
        self.path = path
        self.kind = kind

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


class AccessCondition(dict):
    pass


class ResponseMetadata(dict):
    pass

