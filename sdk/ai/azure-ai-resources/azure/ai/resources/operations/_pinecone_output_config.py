# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# General todo: need to determine which args are required or optional when parsed out into groups like this.
# General todo: move these to more permanent locations?

# Defines stuff related to the resulting created index, like the index type.
class PineconeOutputConfig:
    """Config class for creating a Pinecone index.

    :param pinecone_index_name:
    :type pinecone_index_name: str
    :param pinecone_connection_id:
    :type pinecone_connection_id: str
    """

    def __init__(
        self,
        *,
        pinecone_index_name: str = None,
        pinecone_connection_id: str = None,
    ):
        self.pinecone_index_name = pinecone_index_name
        self.pinecone_connection_id = pinecone_connection_id
