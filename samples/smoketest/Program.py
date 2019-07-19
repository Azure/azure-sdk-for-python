from KeyVaultSecrets import KeyVault
from StorageBlobs import StorageBlob
from EventHubs import EventHub
from CosmosDB import CosmosDB

print("==========================================")
print("      AZURE TRACK 2 SDKs SMOKE TEST")
print("==========================================")

KeyVault().Run()
StorageBlob().Run()
EventHub().Run()
CosmosDB().Run()