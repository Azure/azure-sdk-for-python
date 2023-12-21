# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# General todo: need to determine which args are required or optional when parsed out into groups like this.
# General todo: move these to more permanent locations?

# Defines stuff related to the resulting created index, like the index type.

from typing import Optional

class ACSOutputConfig:
    """Config class for creating an Azure Cognitive Services index.

    :param acs_index_name:
    :type acs_index_name: str
    :param acs_connection_id:
    :type acs_connection_id: str
    :param acs_index_content_key:
    :type acs_index_content_key: str
    :param acs_embedding_key:
    :type acs_embedding_key: str
    :param acs_title_key:
    :type acs_title_key: str
    """

    def __init__(
        self,
        *,
        acs_index_name: Optional[str] = None,
        acs_connection_id: Optional[str] = None,
    ) -> None:
        self.acs_index_name = acs_index_name
        self.acs_connection_id = acs_connection_id
