from azure.core.paging import ItemPaged

class CosmosClient():
    def __init__(self, url, credential, consistency_level=None, **kwargs):
        auth = credential
        connection_policy = "connection_policy"
        self.client_connection = CosmosClientConnection(
            url, auth=auth, consistency_level=consistency_level, connection_policy=connection_policy, **kwargs
        )

    def list_databases(self, **kwargs):
        result = self.client_connection.ReadDatabases(options="", **kwargs)
        return result

class CosmosClientConnection(object):
    def ReadDatabases(self, options=None, **kwargs):
         return self.QueryDatabases(None, options, **kwargs)
         
    def QueryDatabases(self, query, options=None, **kwargs):
        return ItemPaged(
            self, query, options, fetch_function="fetch", page_iterator_class=query
        )