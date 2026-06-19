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

"""Global Secondary Index (GSI) container definition."""

from typing import Optional


class GlobalSecondaryIndexDefinition:
    """**provisional** Definition for a Global Secondary Index (GSI) container.

    A GSI container is a derived container built from a source container
    using a SQL-like projection query. The GSI definition is immutable after creation.

    .. note::
        A maximum of 5 GSI containers can be created per source container.
        All GSI containers must be deleted before deleting the source container.

    :param str source_container_id: The ID of the source container the GSI is derived from. Required.
    :param str definition: The SQL-like projection query that defines the GSI. Required.
    """

    def __init__(self, source_container_id: str, definition: str):
        if not source_container_id or not source_container_id.strip():
            raise ValueError("source_container_id cannot be None or empty.")
        if not definition or not definition.strip():
            raise ValueError("definition cannot be None or empty.")
        self._source_container_id = source_container_id
        self._definition = definition
        self._source_container_rid: Optional[str] = None
        self._status: Optional[str] = None

    @property
    def source_container_id(self) -> str:
        """The ID of the source container.

        :returns: The source container ID.
        :rtype: str
        """
        return self._source_container_id

    @property
    def definition(self) -> str:
        """The SQL-like projection query that defines the GSI.

        :returns: The projection query.
        :rtype: str
        """
        return self._definition

    @property
    def source_container_rid(self) -> Optional[str]:
        """The server-populated resource ID (_rid) of the source container. Read-only.

        :returns: The source container resource ID, or None if not yet populated.
        :rtype: str or None
        """
        return self._source_container_rid

    @property
    def status(self) -> Optional[str]:
        """The GSI build status. Read-only, server-populated.

        Possible values: "Initializing", "InitialBuildAfterCreate",
        "InitialBuildAfterRestore", "Active", "DeleteInProgress"

        :returns: The GSI status, or None if not yet populated.
        :rtype: str or None
        """
        return self._status

    def _to_dict(self) -> dict:
        """Serialize to wire format dict.

        :returns: A dictionary representation of the GSI definition.
        :rtype: dict
        """
        result: dict = {
            "sourceCollectionId": self._source_container_id,
            "definition": self._definition,
        }
        if self._source_container_rid is not None:
            result["sourceCollectionRid"] = self._source_container_rid
        if self._status is not None:
            result["status"] = self._status
        return result

    @classmethod
    def _from_dict(cls, data: Optional[dict]) -> Optional["GlobalSecondaryIndexDefinition"]:
        """Deserialize from wire format dict.

        :param dict data: The wire format dictionary.
        :returns: A GlobalSecondaryIndexDefinition instance, or None if data is None or invalid.
        :rtype: ~azure.cosmos.GlobalSecondaryIndexDefinition or None
        """
        if data is None:
            return None
        source_container_id = data.get("sourceCollectionId")
        definition_query = data.get("definition")
        if not source_container_id or not definition_query:
            return None
        instance = cls(source_container_id, definition_query)
        instance._source_container_rid = data.get("sourceCollectionRid")  # pylint: disable=protected-access
        instance._status = data.get("status")  # pylint: disable=protected-access
        return instance
