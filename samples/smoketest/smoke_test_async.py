import asyncio
from key_vault_secrets_async import KeyVault_async
from event_hubs_async import EventHub_async

print("")
print("==========================================")
print("   AZURE TRACK 2 SDKs SMOKE TEST ASYNC")
print("==========================================")


async def main():
    await KeyVault_async().run()
    await EventHub_async().run()


loop = asyncio.get_event_loop()

task = loop.create_task(main())
loop.run_until_complete(task)
