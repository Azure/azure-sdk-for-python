def delete_database(database_id):
    import azure.cosmos.cosmos_client as cosmos_client
    import azure.cosmos.exceptions as exceptions
    import test_config

    print("Cleaning up test resources.")
    config = test_config._test_config
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    try:
        client = cosmos_client.CosmosClient(host, masterKey, "Session", connection_policy=connectionPolicy)
    # This is to soft-fail the teardown while cosmos tests are not running automatically
    except Exception as exception:
        print("Error while initialing the client", exception)
        pass
    else:
        try:
            print("Deleting database with id : ", database_id)
            client.delete_database(database_id)
            print("Deleted : ", database_id)
        except exceptions.CosmosResourceNotFoundError as exception:
            print("Error while deleting database", exception)
            pass
    print("Clean up completed!")


if __name__== "__main__":
    import sys
    if len(sys.argv) < 2:
        raise ValueError("database_id for deletion not provided.")
    import os.path as path
    root_path = path.abspath(path.join(__file__, "..", ".."))
    sys.path.append(root_path)
    database_id = sys.argv[1]
    delete_database(database_id)
