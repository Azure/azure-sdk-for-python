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

import six
from .cosmos_client_connection import CosmosClientConnection
from typing import (
    Any,
    List,
    Dict,
    Union,
    cast
)
from .permission import Permission


class User:

    def __init__(self, client_connection, id, database_link, properties=None):
        # type: (CosmosClientConnection, str, str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.id = id
        self.user_link = u"{}/users/{}".format(database_link, id)
        self._properties = properties

    def _get_permission_link(self, permission_or_id):
        # type: (Union[Permission, str, Dict[str, Any]]) -> str
        if isinstance(permission_or_id, six.string_types):
            return u"{}/permissions/{}".format(self.user_link, permission_or_id)
        try:
            return cast("Permission", permission_or_id).permission_link
        except AttributeError:
            pass
        return u"{}/permissions/{}".format(self.user_link, cast("Dict[str, str]", permission_or_id)["id"])

    def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self.read()
        return self._properties

    def read(
            self,
            request_options=None
    ):
        # type: (Dict[str, Any]) -> User
        """
        Read user propertes.

        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`User` instance representing the retrieved user.
        :raise `HTTPFailure`: If the given user couldn't be retrieved.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        self._properties = self.client_connection.ReadUser(
            user_link=self.user_link,
            options=request_options
        )
        return self._properties

    def list_permission_properties(
            self,
            max_item_count=None,
            feed_options=None
    ):
        # type: (int, Dict[str, Any]) -> QueryIterable
        """ List all permission for the user.

        :param max_item_count: Max number of permissions to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of permissions (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.ReadPermissions(
            user_link=self.user_link,
            options=feed_options
        )

    def query_permissions(
            self,
            query,
            parameters=None,
            max_item_count=None,
            feed_options=None
    ):
        # type: (str, List, int, Dict[str, Any]) -> QueryIterable
        """Return all permissions matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of permissions to be returned in the enumeration operation.
        :param feed_options: Dictionary of additional properties to be used for the request.
        :returns: A :class:`QueryIterable` instance representing an iterable of permissions (dicts).

        """
        if not feed_options:
            feed_options = {} # type: Dict[str, Any]
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        return self.client_connection.QueryPermissions(
            user_link=self.user_link,
            query=query
            if parameters is None
            else dict(query=query, parameters=parameters),
            options=feed_options,
        )

    def get_permission(
            self,
            permission,
            request_options=None
    ):
        # type: (str, Dict[str, Any]) -> Permission
        """
        Get the permission identified by `id`.

        :param permission: The ID (name), dict representing the properties or :class:`Permission` instance of the permission to be retrieved.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the retrieved permission.
        :raise `HTTPFailure`: If the given permission couldn't be retrieved.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        permission = self.client_connection.ReadPermission(
            permission_link=self._get_permission_link(permission),
            options=request_options
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def create_permission(
            self,
            body,
            request_options=None
    ):
        # type: (Dict[str, Any], Dict[str, Any]) -> Permission
        """ Create a permission for the user.

        :param body: A dict-like object representing the permission to create.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the new permission.
        :raise `HTTPFailure`: If the given permission couldn't be created.

        To update or replace an existing permision, use the :func:`User.upsert_permission` method.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        permission = self.client_connection.CreatePermission(
            user_link=self.user_link,
            permission=body,
            options=request_options
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def upsert_permission(
            self,
            body,
            request_options=None
    ):
        # type: (Dict[str, Any], Dict[str, Any]) -> Permission
        """ Insert or update the specified permission.

        :param body: A dict-like object representing the permission to update or insert.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the upserted permission.
        :raise `HTTPFailure`: If the given permission could not be upserted.

        If the permission already exists in the container, it is replaced. If it does not, it is inserted.
        """

        if not request_options:
            request_options = {} # type: Dict[str, Any]

        permission = self.client_connection.UpsertPermission(
            user_link=self.user_link,
            permission=body,
            options=request_options
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def replace_permission(
            self,
            permission,
            body,
            request_options=None
    ):
        # type: (str, Dict[str, Any], Dict[str, Any]) -> Permission
        """ Replaces the specified permission if it exists for the user.

        :param permission: The ID (name), dict representing the properties or :class:`Permission` instance of the permission to be replaced.
        :param body: A dict-like object representing the permission to replace.
        :param request_options: Dictionary of additional properties to be used for the request.
        :returns: A dict representing the permission after replace went through.
        :raise `HTTPFailure`: If the replace failed or the permission with given id does not exist.

        """
        if not request_options:
            request_options = {} # type: Dict[str, Any]

        permission = self.client_connection.ReplacePermission(
            permission_link=self._get_permission_link(permission),
            permission=body,
            options=request_options
        )

        return Permission(
            id=permission['id'],
            user_link=self.user_link,
            permission_mode=permission['permissionMode'],
            resource_link=permission['resource'],
            properties=permission
        )

    def delete_permission(
            self,
            permission,
            request_options=None
    ):
        # type: (str, Dict[str, Any]) -> None
        """ Delete the specified permission from the user.

        :param permission: The ID (name), dict representing the properties or :class:`Permission` instance of the permission to be replaced.
        :param request_options: Dictionary of additional properties to be used for the request.
        :raises `HTTPFailure`: The permission wasn't deleted successfully. If the permission does not exist for the user, a `404` error is returned.

        """

        if not request_options:
            request_options = {} # type: Dict[str, Any]

        self.client_connection.DeletePermission(
            permission_link=self._get_permission_link(permission),
            options=request_options
        )

