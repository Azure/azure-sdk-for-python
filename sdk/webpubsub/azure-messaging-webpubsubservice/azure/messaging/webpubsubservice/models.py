from typing import Optional
import json

class GroupMember:
    """Represents a member in a group.

    :param connection_id: A unique identifier of a connection.
    :type connection_id: str
    :param user_id: The user ID of the connection. A user can have multiple connections.
    :type user_id: Optional[str]
    """

    def __init__(self, connection_id: str, user_id: Optional[str] = None) -> None:
        self._connection_id = connection_id
        self._user_id = user_id

    @property
    def connection_id(self) -> str:
        """Gets the connection ID.

        :return: The connection ID.
        :rtype: str
        """
        return self._connection_id

    @property
    def user_id(self) -> Optional[str]:
        """Gets the user ID.

        :return: The user ID.
        :rtype: Optional[str]
        """
        return self._user_id

    def __repr__(self) -> str:
        return json.dumps({
            "connection_id": self._connection_id,
            "user_id": self._user_id
        })

