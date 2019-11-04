# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from key_vault_secrets import KeyVaultSecrets
from storage_blob import StorageBlob
from event_hubs import EventHub
from cosmos_db import CosmosDB

print("")
print("==========================================")
print("      AZURE TRACK 2 SDKs SMOKE TEST")
print("==========================================")

KeyVaultSecrets().run()
StorageBlob().run()
EventHub().run()
CosmosDB().run()
