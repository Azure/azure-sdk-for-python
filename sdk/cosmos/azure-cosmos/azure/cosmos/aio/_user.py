# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

from typing import Any, Dict, List, Mapping, Union, Optional

from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace

from ._cosmos_client_connection_async import CosmosClientConnection
from .._base import build_options
from ..permission import Permission


class UserProxy:
    """An interface to interact with a specific user.

    This class should not be instantiated directly. Instead, use the
    :func:`DatabaseProxy.get_user_client` method.

    :ivar str id:
    :ivar str user_link:
    """

    def __init__(
        self,
        client_connection: CosmosClientConnection,
        id: str,
        database_link: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        self.client_connection = client_connection
        self.id = id
        self.user_link = "{}/users/{}".format(database_link, id)
        self._properties = properties

    def __repr__(self) -> str:
        return "<UserProxy [{}]>".format(self.user_link)[:1024]

    def _get_permission_link(self, permission_or_id: Union[Permission, str, Mapping[str, Any]]) -> str:
        if isinstance(permission_or_id, str):
            return "{}/permissions/{}".format(self.user_link, permission_or_id)
        if isinstance(permission_or_id, Permission):
            return permission_or_id.permission_link
        return "{}/permissions/{}".format(self.user_link, permission_or_id["id"])

    async def _get_properties(self) -> Dict[str, Any]:
        if self._properties is None:
            self._properties = await self.read()
        return self._properties

    @distributed_trace_async
    async def read(self, **kwargs: Any) -> Dict[str, Any]:
        """Read user properties.

        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given user couldn't be retrieved.
        :returns: A dictionary of the retrieved user properties.
        :rtype: Dict[str, Any]
        """
        request_options = build_options(kwargs)

        self._properties = await self.client_connection.ReadUser(
            user_link=self.user_link,
            options=request_options,
            **kwargs
        )
        return self._properties

    @distributed_trace
    def list_permissions(
        self,
        *,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """List all permission for the user.

        :keyword int max_item_count: Max number of permissions to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]], None]
        :returns: An AsyncItemPaged of permissions (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
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
        query: str,
        *,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_item_count: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncItemPaged[Dict[str, Any]]:
        """Return all permissions matching the given `query`.

        :param str query: The Azure Cosmos DB SQL query to execute.
        :keyword parameters: Optional array of parameters to the query. Ignored if no query is provided.
        :paramtype parameters: Optional[List[Dict[str, Any]]]
        :keyword int max_item_count: Max number of permissions to be returned in the enumeration operation.
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], AsyncItemPaged[Dict[str, Any]]], None]
        :returns: An AsyncItemPaged of permissions (dicts).
        :rtype: AsyncItemPaged[Dict[str, Any]]
        """
        feed_options = build_options(kwargs)
        response_hook = kwargs.pop('response_hook', None)
        if max_item_count is not None:
            feed_options["maxItemCount"] = max_item_count

        result = self.client_connection.QueryPermissions(
            user_link=self.user_link,
            query=query if parameters is None else {"query": query, "parameters": parameters},
            options=feed_options,
            **kwargs
        )

        if response_hook:
            response_hook(self.client_connection.last_response_headers, result)

        return result

    @distributed_trace_async
    async def get_permission(
        self,
        permission: Union[str, Mapping[str, Any], Permission],
        **kwargs: Any
    ) -> Permission:
        """Get the permission identified by `id`.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be retrieved.
        :type permission: Union[str, Dict[str, Any], ~azure.cosmos.Permission]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission couldn't be retrieved.
        :returns: The retrieved permission object.
        :rtype: ~azure.cosmos.Permission
        """
        request_options = build_options(kwargs)

        permission_resp = await self.client_connection.ReadPermission(
            permission_link=self._get_permission_link(permission), options=request_options, **kwargs
        )
        return Permission(
            id=permission_resp["id"],
            user_link=self.user_link,
            permission_mode=permission_resp["permissionMode"],
            resource_link=permission_resp["resource"],
            properties=permission_resp,
        )

    @distributed_trace_async
    async def create_permission(self, body: Dict[str, Any], **kwargs: Any) -> Permission:
        """Create a permission for the user.

        To update or replace an existing permission, use the :func:`UserProxy.upsert_permission` method.

        :param body: A dict-like object representing the permission to create.
        :type body: Dict[str, Any]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission couldn't be created.
        :returns: A permission object representing the new permission.
        :rtype: ~azure.cosmos.Permission
        """
        request_options = build_options(kwargs)

        permission = await self.client_connection.CreatePermission(
            user_link=self.user_link, permission=body, options=request_options, **kwargs
        )

        return Permission(
            id=permission["id"],
            user_link=self.user_link,
            permission_mode=permission["permissionMode"],
            resource_link=permission["resource"],
            properties=permission,
        )

    @distributed_trace_async
    async def upsert_permission(self, body: Dict[str, Any], **kwargs: Any) -> Permission:
        """Insert or update the specified permission.

        If the permission already exists in the container, it is replaced. If
        the permission does not exist, it is inserted.

        :param body: A dict-like object representing the permission to update or insert.
        :type body: Dict[str, Any]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the given permission could not be upserted.
        :returns: A dict representing the upserted permission.
        :rtype: ~azure.cosmos.Permission
        """
        request_options = build_options(kwargs)

        permission = await self.client_connection.UpsertPermission(
            user_link=self.user_link, permission=body, options=request_options, **kwargs
        )

        return Permission(
            id=permission["id"],
            user_link=self.user_link,
            permission_mode=permission["permissionMode"],
            resource_link=permission["resource"],
            properties=permission,
        )

    @distributed_trace_async
    async def replace_permission(
        self,
        permission: Union[str, Mapping[str, Any], Permission],
        body: Dict[str, Any],
        **kwargs: Any
    ) -> Permission:
        """Replaces the specified permission if it exists for the user.

        If the permission does not already exist, an exception is raised.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be replaced.
        :type permission: Union[str, Dict[str, Any], ~azure.cosmos.Permission]
        :param body: A dict-like object representing the permission to replace.
        :type body: Dict[str, Any]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], Dict[str, Any]], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: If the replace operation failed or the permission
            with given id does not exist.
        :returns: A permission object representing the permission after the replace operation went through.
        :rtype: ~azure.cosmos.Permission
        """
        request_options = build_options(kwargs)

        permission_resp = await self.client_connection.ReplacePermission(
            permission_link=self._get_permission_link(permission), permission=body, options=request_options, **kwargs
        )  # type: Dict[str, str]

        return Permission(
            id=permission_resp["id"],
            user_link=self.user_link,
            permission_mode=permission_resp["permissionMode"],
            resource_link=permission_resp["resource"],
            properties=permission_resp,
        )

    @distributed_trace_async
    async def delete_permission(
        self,
        permission: Union[str, Mapping[str, Any], Permission],
        **kwargs: Any
    ) -> None:
        """Delete the specified permission from the user.

        If the permission does not already exist, an exception is raised.

        :param permission: The ID (name), dict representing the properties or :class:`Permission`
            instance of the permission to be deleted.
        :type permission: Union[str, Dict[str, Any], ~azure.cosmos.Permission]
        :keyword response_hook: A callable invoked with the response metadata.
        :paramtype response_hook: Callable[[Dict[str, str], None], None]
        :raises ~azure.cosmos.exceptions.CosmosHttpResponseError: The permission wasn't deleted successfully.
        :raises ~azure.cosmos.exceptions.CosmosResourceNotFoundError: The permission does not exist for the user.
        :rtype: None
        """
        request_options = build_options(kwargs)

        await self.client_connection.DeletePermission(
            permission_link=self._get_permission_link(permission), options=request_options, **kwargs
        )
