import azure.cosmos.cosmos_client as cosmos_client
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to pass in values for the connection policy retry options.
#
# 1. retry_connect option determines how many connection-related errors to retry on.
#
# 2. retry_read option determines how many times to retry on read errors.
#
# 3. retry_status determines how many times to retry on bad status codes.
#
# 4. retry_on_status_codes is a list of specific status codes to retry on
#
# 5. retry_backoff_factor is a factor to calculate wait time between retry attempts.
# ----------------------------------------------------------------------------------------------------------

def change_connection_retry_policy_configs():
    cosmos_client.CosmosClient(url=HOST, credential=MASTER_KEY, retry_connect=4,
                               retry_read=5, retry_status=2,
                               retry_on_status_codes=([404, 429]),
                               retry_backoff_factor=.09)


if __name__ == "__main__":
    change_connection_retry_policy_configs()
