# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# General todo: need to determine which args are required or optional when parsed out into groups like this.
# General todo: move these to more permanent locations?

# Defines stuff related to the resulting created index, like the index type.

from typing import Optional
from azure.ai.ml._utils._experimental import experimental


@experimental
class AzureAISearchConfig:
    """Config class for creating an Azure AI Search index.

    :param index_name: The name of the Azure AI Search index.
    :type index_name: Optional[str]
    :param connection_id: The Azure AI Search connection ID.
    :type connection_id: Optional[str]
    """

    def __init__(
        self,
        *,
        index_name: Optional[str] = None,
        connection_id: Optional[str] = None,
    ) -> None:
        self.index_name = index_name
        self.connection_id = connection_id
