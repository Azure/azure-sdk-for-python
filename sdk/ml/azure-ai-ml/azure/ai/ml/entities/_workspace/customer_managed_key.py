# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class CustomerManagedKey:
    def __init__(
        self,
        key_vault: str = None,
        key_uri: str = None,
        cosmosdb_id: str = None,
        storage_id: str = None,
        search_id: str = None,
    ):
        self.key_vault = key_vault
        self.key_uri = key_uri
        self.cosmosdb_id = cosmosdb_id or ""
        self.storage_id = storage_id or ""
        self.search_id = search_id or ""
