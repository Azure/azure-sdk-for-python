# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from microsoft.opentelemetry.exporter.azuremonitor._utils import BaseObject

__all__ = ["ExporterOptions"]


class ExporterOptions(BaseObject):
    """Configuration for Azure Exporters.
    :param str connection_string: Azure Connection String.
    """

    __slots__ = (
        "connection_string",
    )

    def __init__(
        self,
        connection_string: str = None
    ) -> None:
        self.connection_string = connection_string
