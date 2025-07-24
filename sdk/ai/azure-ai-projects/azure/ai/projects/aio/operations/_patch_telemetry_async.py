# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, AsyncIterable
from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator_async import distributed_trace_async

from ...models._models import (
    Connection,
    ApiKeyCredentials,
)
from ...models._enums import ConnectionType


class TelemetryOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`telemetry` attribute.
    """

    _connection_string: Optional[str] = None

    def __init__(self, outer_instance: "azure.ai.projects.aio.AIProjectClient") -> None:  # type: ignore[name-defined]
        self._outer_instance = outer_instance

    @distributed_trace_async
    async def get_application_insights_connection_string(self) -> str:  # pylint: disable=name-too-long
        """Get the Application Insights connection string associated with the Project's Application Insights resource.

        :return: The Application Insights connection string if a the resource was enabled for the Project.
        :rtype: str
        :raises ~azure.core.exceptions.ResourceNotFoundError: An Application Insights connection does not
            exist for this Foundry project.
        """
        if not self._connection_string:

            # TODO: Two REST APIs calls can be replaced by one if we have had REST API for get_with_credentials(connection_type=ConnectionType.APPLICATION_INSIGHTS)
            # Returns an empty Iterable if no connections exits.
            connections: AsyncIterable[Connection] = self._outer_instance.connections.list(
                connection_type=ConnectionType.APPLICATION_INSIGHTS,
            )

            # Note: there can't be more than one AppInsights connection.
            connection_name: Optional[str] = None
            async for connection in connections:
                connection_name = connection.name
                break
            if not connection_name:
                raise ResourceNotFoundError("No Application Insights connection found.")

            connection = (
                await self._outer_instance.connections._get_with_credentials(  # pylint: disable=protected-access
                    name=connection_name
                )
            )

            if isinstance(connection.credentials, ApiKeyCredentials):
                if not connection.credentials.api_key:
                    raise ValueError("Application Insights connection does not have a connection string.")
                self._connection_string = connection.credentials.api_key
            else:
                raise ValueError("Application Insights connection does not use API Key credentials.")

        return self._connection_string
