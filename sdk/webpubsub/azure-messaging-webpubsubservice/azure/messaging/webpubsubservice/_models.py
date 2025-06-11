from typing import Optional, Any

class GroupMember:
    """Represents a member in a group.

    :param connection_id: A unique identifier of a connection.
    :type connection_id: str
    :param user_id: The user ID of the connection. A user can have multiple connections.
    :type user_id: Optional[str]
    """

    connection_id: str
    user_id: Optional[str]

    def __init__(self, **kwargs: Any) -> None:
        self.connection_id = kwargs['connection_id']
        self.user_id = kwargs.get('user_id')

    def __repr__(self) -> str:
        return f"GroupMember(connection_id='{self.connection_id}', user_id='{self.user_id}')"
