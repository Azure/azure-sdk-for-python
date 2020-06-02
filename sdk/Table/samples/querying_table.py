from azure.azure_table._generated.models import QueryOptions


class QueryTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="
    # query tables by some filter type
    query_options = QueryOptions("name")

    def list_tables(self):
        from azure.azure_table import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        tables = list(table_client.list_tables())
        print(tables)

    def query_tables(self):
        from azure.azure_table import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        queried_tables = list(table_client.query_tables(query_options=self.query_options))
        print(queried_tables)
