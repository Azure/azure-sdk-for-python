# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Optional


class CustomerManagedKey:
    """Key vault details for encrypting data with customer-managed keys.

    :param key_vault: Key vault that is holding the customer-managed key.
    :type key_vault: str
    :param key_uri: URI for the customer-managed key.
    :type key_uri: str
    :param cosmosdb_id: ARM id of bring-your-own cosmosdb account that customer brings
        to store customer's data with encryption.
    :type cosmosdb_id: str
    :param storage_id: ARM id of bring-your-own storage account that customer brings
        to store customer's data with encryption.
    :type storage_id: str
    :param search_id: ARM id of bring-your-own search account that customer brings
        to store customer's data with encryption.
    :type search_id: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START customermanagedkey]
            :end-before: [END customermanagedkey]
            :language: python
            :dedent: 8
            :caption: Creating a CustomerManagedKey object.
    """

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
