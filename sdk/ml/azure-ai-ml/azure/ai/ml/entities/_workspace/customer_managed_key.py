# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Optional


class CustomerManagedKey:
    def __init__(
        self,
        key_vault: Optional[str] = None,
        key_uri: Optional[str] = None,
        cosmosdb_id: Optional[str] = None,
        storage_id: Optional[str] = None,
        search_id: Optional[str] = None,
    ):
        self.key_vault = key_vault
        self.key_uri = key_uri
        self.cosmosdb_id = cosmosdb_id or ""
        self.storage_id = storage_id or ""
        self.search_id = search_id or ""
