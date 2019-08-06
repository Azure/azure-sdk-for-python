# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from key_vault_secrets_async import KeyVault
from event_hubs_async import EventHub

print("")
print("==========================================")
print("   AZURE TRACK 2 SDKs SMOKE TEST ASYNC")
print("==========================================")


async def main():
    await KeyVault().run()
    await EventHub().run()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
