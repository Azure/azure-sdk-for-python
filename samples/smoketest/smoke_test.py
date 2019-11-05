# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from key_vault_secrets import KeyVaultSecrets
from key_vault_keys import KeyVaultKeys
from key_vault_certificates import KeyVaultCertificates
from storage_blob import StorageBlob
from event_hubs import EventHub
from cosmos_db import CosmosDB

print("")
print("==========================================")
print("      AZURE TRACK 2 SDKs SMOKE TEST")
print("==========================================")

KeyVaultSecrets().run()
KeyVaultKeys().run()
KeyVaultCertificates().run()
StorageBlob().run()
EventHub().run()
CosmosDB().run()
