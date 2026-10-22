# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from key_vault_certificates import KeyVaultCertificates
from key_vault_keys import KeyVaultKeys
from key_vault_secrets import KeyVaultSecrets
from storage_blob import StorageBlob
from event_hubs import EventHub

# Temporarily disable cosmos smoke tests
# from cosmos_db import CosmosDB

def execute_smoke_tests():
    print("")
    print("==========================================")
    print("      AZURE TRACK 2 SDKs SMOKE TEST")
    print("==========================================")

    KeyVaultCertificates().run()
    KeyVaultKeys().run()
    KeyVaultSecrets().run()
    StorageBlob().run()
    EventHub().run()

    # Temporarily disable cosmos smoke tests
    # CosmosDB().run()
