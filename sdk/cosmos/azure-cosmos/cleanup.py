import sys
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test.test_config as test_config

def delete_database(database_id):
    print("Cleaning up test resources.")
    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    try:
        client = cosmos_client.CosmosClient(host, masterKey, "Session", connection_policy=connectionPolicy)
    # This is to soft-fail the teardown while cosmos tests are not running automatically
    except Exception:
        pass
    else:
        try:
            client.delete_database(database_id)
            print("Deleted " + database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
    print("Clean up completed!")


if __name__== "__main__":
    if len(sys.argv) < 2:
        raise ValueError("database_id for deletion not provided.")
    database_id = sys.argv[1]
    delete_database(database_id)
