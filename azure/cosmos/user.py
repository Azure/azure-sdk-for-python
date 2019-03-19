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

"""Create, read, update and delete permissions in the Azure Cosmos DB SQL API service.
"""

from .permission import Permission

class User:

    def __init__(self, client_connection, id, database_link, properties):
        # type: (CosmosClientConnection, str, str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.id = id
        self.user_link = u"{}/users/{}".format(database_link, id)
        self.properties = properties

    def _get_permission_link(self, id):
        # type: (str) -> str
        return u"{}/permissions/{}".format(self.user_link, id)

    def list_permissions(self, max_item_count=None):
        # type: (int) -> QueryIterable
        """ List all permission for the user.

        :param max_item_count: Max number of permissions to be returned in the enumeration operation.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadPermissions(
            user_link=self.user_link,
            options=request_options
        )

    def query_permissions(self, query, parameters=None, max_item_count=None):
        # type: (str, List, int) -> QueryIterable
        """Return all permissions matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of permissions to be returned in the enumeration operation.
        :returns: An `Iterator` containing each result returned by the query, if any.

        """
        request_options = {}  # type: Dict[str, Any]
        if max_item_count is not None:
            request_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryPermissions(
            user_link=self.user_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=request_options,
        )

    def get_permission(self, id):
        # type: (str) -> Permission
        """
        Get the permission identified by `id`.

        :param id: ID of the permission to be retrieved.
        :returns: The permission as a dict, if present in the container.

        """
        permission = self.client_connection.ReadPermission(
            permission_link=self._get_permission_link(id)
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def create_permission(self, body):
        # type: (Dict[str, Any]) -> Permission
        """ Create a permission for the user.

        :param body: A dict-like object representing the permission to create.
        :raises `HTTPFailure`:

        To update or replace an existing permision, use the :func:`User.upsert_permission` method.

        """
        permission = self.client_connection.CreatePermission(
            user_link=self.user_link,
            permission=body
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def upsert_permission(self, body):
        # type: (Dict[str, Any]) -> Permission
        """ Insert or update the specified permission.

        :param body: A dict-like object representing the permission to update or insert.
        :raises `HTTPFailure`:

        If the permission already exists in the container, it is replaced. If it does not, it is inserted.
        """

        permission = self.client_connection.UpsertPermission(
            user_link=self.user_link,
            permission=body
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def replace_permission(self, id, body):
        # type: (str, Dict[str, Any]) -> Permission
        """ Replaces the specified permission if it exists for the user.

        :param id: Id of the permission to be replaced.
        :param body: A dict-like object representing the permission to replace.
        :raises `HTTPFailure`:

        """
        permission = self.client_connection.ReplacePermission(
            permission_link=self._get_permission_link(id),
            permission=body
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def delete_permission(self, id):
        # type: (str) -> None
        """ Delete the specified permission from the user.

        :param id: Id of the permission to delete from the container.
        :raises `HTTPFailure`: The permission wasn't deleted successfully. If the permission does not exist for the user, a `404` error is returned.

        """

        self.client_connection.DeletePermission(
            permission_link=self._get_permission_link(id)
        )

