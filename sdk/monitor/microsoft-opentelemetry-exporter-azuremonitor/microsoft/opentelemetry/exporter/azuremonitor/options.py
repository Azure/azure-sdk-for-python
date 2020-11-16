# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

class ExporterOptions:
    """Options to configure Azure exporters.

    Args:
        connection_string: Azure Connection String.
    """

    def __init__(
        self,
        connection_string: str = None
    ) -> None:
        self.connection_string = connection_string
