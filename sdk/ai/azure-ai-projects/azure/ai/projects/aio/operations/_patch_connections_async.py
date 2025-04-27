# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional
from azure.core.tracing.decorator_async import distributed_trace_async

from ._operations import ConnectionsOperations as ConnectionsOperationsGenerated
from ...models._models import Connection


class ConnectionsOperations(ConnectionsOperationsGenerated):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`connections` attribute.
    """
    
    @distributed_trace_async
    async def get(self, name: str, *, include_credentials: Optional[bool] = False, **kwargs: Any) -> Connection:
        """Get a connection by name.

        :param name: The name of the resource. Required.
        :type name: str
        :keyword include_credentials: Whether to include credentials in the response. Default is False.
        :paramtype include_credentials: bool
        :return: Connection. The Connection is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.Connection
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if include_credentials:
            return await super()._get_with_credentials(name, **kwargs)
        else:
            return await super()._get(name, **kwargs)


