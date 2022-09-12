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

# pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs

"""Create, read, update and delete users in the Azure Cosmos DB SQL API service.
"""

from typing import Any, List, Dict, Union, cast, Iterable, Optional

from azure.core.tracing.decorator import distributed_trace  # type: ignore

from ._cosmos_client_connection import CosmosClientConnection
from ._base import build_options
from .permission import Permission


class UserProxy(object):
    """An interface to interact with a specific user.

    This class should not be instantiated directly. Instead, use the
    :func:`DatabaseProxy.get_user_client` method.
    """

    def __init__(self, client_connection, id, database_link, properties=None):  # pylint: disable=redefined-builtin
        # type: (CosmosClientConnection, str, str, Dict[str, Any]) -> None
        self.client_connection = client_connection
        self.id = id
        self.user_link = u"{}/users/{}".format(database_link, id)
        self._properties = properties

    def __repr__(self):
        # type () -> str
        return "<UserProxy [{}]>".format(self.user_link)[:1024]

    def _get_permission_link(self, permission_or_id):
        # type: (Union[Permission, str, Dict[str, Any]]) -> str
        if isinstance(permission_or_id, str):
            return u"{}/permissions/{}".format(self.user_link, permission_or_id)
        try:
            return cast("Permission", permission_or_id).permission_link
        except AttributeError:
            pass
        return u"{}/permissions/{}".format(self.user_link, cast("Dict[str, str]", permission_or_id)["id"])

    def _get_properties(self):
        # type: () -> Dict[str, Any]
        if self._properties is None:
            self._properties = self.read()
        return self._properties

    @distributed_trace
    def read(self, **kwargs):
        # type: (Any) -> Dict[str, Any]
        """Read user properties.

        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dictionary of the retrieved user properties.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user couldn't be retrieved.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        self._properties = self.client_connection.ReadUser(user_link=self.user_link, options=request_options, **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, self._properties)

        return cast('Dict[str, Any]', self._properties)

    @distributed_trace
    def list_permissions(self, max_item_count=None, **kwargs):
        # type: (Optional[int], Any) -> Iterable[Dict[str, Any]]
        """List all permission for the user.

        :param max_item_count: Max number of permissions to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of permissions (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.ReadPermissions(user_link=self.user_link, options=feed_options, **kwargs)

        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

        return result

    @distributed_trace
    def query_permissions(
        self,
        query,
        parameters=None,
        max_item_count=None,
        **kwargs
    ):
        # type: (str, Optional[List[str]], Optional[int], Any) -> Iterable[Dict[str, Any]]
        """Return all permissions matching the given `query`.

        :param query: The Azure Cosmos DB SQL query to execute.
        :param parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :param max_item_count: Max number of permissions to be returned in the enumeration operation.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: An Iterable of permissions (dicts).
        :rtype: Iterable[dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryPermissions(
            user_link=self.user_link,
            query=query if parameters is None else dict(query=query, parameters=parameters),
            options=feed_options,
            **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

        return result

    @distributed_trace
    def get_permission(self, permission, **kwargs):
        # type: (str, Any) -> Permission
        """Get the permission identified by `id`.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be retrieved.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the retrieved permission.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission couldn't be retrieved.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        permission_resp = self.client_connection.ReadPermission(
            permission_link=self._get_permission_link(permission), options=request_options, **kwargs
        )  # type: Dict[str, str]

        if response_hook:
            response_hook(self.client_connection.last_response_headers, permission_resp)

        return Permission(
            id=permission_resp["id"],
            user_link=self.user_link,
            permission_mode=permission_resp["permissionMode"],
            resource_link=permission_resp["resource"],
            properties=permission_resp,
        )

    @distributed_trace
    def create_permission(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> Permission
        """Create a permission for the user.

        To update or replace an existing permision, use the :func:`UserProxy.upsert_permission` method.

        :param body: A dict-like object representing the permission to create.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the new permission.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission couldn't be created.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        permission = self.client_connection.CreatePermission(
            user_link=self.user_link, permission=body, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, permission)

        return Permission(
            id=permission["id"],
            user_link=self.user_link,
            permission_mode=permission["permissionMode"],
            resource_link=permission["resource"],
            properties=permission,
        )

    @distributed_trace
    def upsert_permission(self, body, **kwargs):
        # type: (Dict[str, Any], Any) -> Permission
        """Insert or update the specified permission.

        If the permission already exists in the container, it is replaced. If
        the permission does not exist, it is inserted.

        :param body: A dict-like object representing the permission to update or insert.
        :param Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the upserted permission.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission could not be upserted.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        permission = self.client_connection.UpsertPermission(
            user_link=self.user_link, permission=body, options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, permission)

        return Permission(
            id=permission["id"],
            user_link=self.user_link,
            permission_mode=permission["permissionMode"],
            resource_link=permission["resource"],
            properties=permission,
        )

    @distributed_trace
    def replace_permission(self, permission, body, **kwargs):
        # type: (str, Dict[str, Any], Any) -> Permission
        """Replaces the specified permission if it exists for the user.

        If the permission does not already exist, an exception is raised.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be replaced.
        :param body: A dict-like object representing the permission to replace.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :returns: A dict representing the permission after replace went through.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace failed or the permission
            with given id does not exist.
        :rtype: dict[str, Any]
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        permission_resp = self.client_connection.ReplacePermission(
            permission_link=self._get_permission_link(permission), permission=body, options=request_options, **kwargs
        )  # type: Dict[str, str]

        if response_hook:
            response_hook(self.client_connection.last_response_headers, permission_resp)

        return Permission(
            id=permission_resp["id"],
            user_link=self.user_link,
            permission_mode=permission_resp["permissionMode"],
            resource_link=permission_resp["resource"],
            properties=permission_resp,
        )

    @distributed_trace
    def delete_permission(self, permission, **kwargs):
        # type: (str, Any) -> None
        """Delete the specified permission from the user.

        If the permission does not already exist, an exception is raised.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be replaced.
        :keyword Callable response_hook: A callable invoked with the response metadata.
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The permission wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The permission does not exist for the user.
        :rtype: None
        """
        request_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)

        result = self.client_connection.DeletePermission(
            permission_link=self._get_permission_link(permission), options=request_options, **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)
