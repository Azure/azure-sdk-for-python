from azure.cosmos.aio import CosmosClient
import config
import asyncio

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to pass in values for the connection policy retry options.
#
# 1. retry_total is the total number of retries to allow. Takes precedence over other counts.
#    Pass in retry_total=0 if you do not want to retry on requests. Default value is 10
#
# 2. retry_connect option determines how many connection-related errors to retry on. Default value is 3
#
# 3. retry_read option determines how many times to retry on read errors. Default value is 3
#
# 4. retry_status determines how many times to retry on bad status codes. Default value is 3
#
# 5. retry_on_status_codes is a list of specific status codes to retry on. The default value is an empty list as the
#    SDK has its own retry logic already configured where this is option is taken care of.
#
# 6. retry_backoff_factor is a factor to calculate wait time between retry attempts. Defaults to .08 seconds
#
# 7. retry_backoff_max option determines the maximum back off time. Default value is 120 seconds (2 minutes)
#
# 8. retry_fixed_interval option determines the fixed retry interval in milliseconds.
#    The default value is None as the SDK has its own retry logic configured where this option is taken care of.
#
# Note:
# While these options can be configured, the SDK by default already has retry mechanisms and we recommend to use those.
# ----------------------------------------------------------------------------------------------------------

async def change_connection_retry_policy_configs():
    async with CosmosClient(url=HOST, credential=MASTER_KEY, retry_total=10, retry_connect=3,
                               retry_read=3, retry_status=3,
                               retry_on_status_codes=([]),
                               retry_backoff_factor=.08, retry_backoff_max=120, retry_fixed_interval=None) as client:
        print('Client initialized with custom retry options')


if __name__ == "__main__":
    asyncio.run(change_connection_retry_policy_configs())
