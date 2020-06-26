from azure.table._generated.models import QueryOptions


class QueryTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # Creating query filter for that table
    table_name = "Office Supplies"
    name_filter = "TableName eq '{}'".format(table_name)
    query_options = QueryOptions(filter=name_filter)

    def list_tables(self):
        from azure.table import TableServiceClient

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        tables = table_service_client.list_tables()
        # table_client.list_tables() returns an itemPaged
        # tables is a list of tables

        for table in tables:
            print(table.table_name)

    def query_tables(self):
        from azure.table import TableServiceClient

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        queried_tables = table_service_client.query_tables(query_options=self.name_filter)
        # table_client.query_tables() returns an itemPaged
        # queried_tables is a list of filtered tables

        for table in queried_tables:
            print(table.table_name)
