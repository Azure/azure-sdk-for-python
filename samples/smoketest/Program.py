from key_vault_secrets import KeyVault
from storage_blob import StorageBlob
from event_hubs import EventHub
from cosmos_db import CosmosDB

print("==========================================")
print("      AZURE TRACK 2 SDKs SMOKE TEST")
print("==========================================")

KeyVault().Run()
StorageBlob().Run()
EventHub().Run()
CosmosDB().Run()
