class QueryTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # Creating query filter for that table
    table_name = "Office Supplies"
    name_filter = "TableName eq '{}'".format(table_name)

    def query_tables(self):
        from azure.table import TableServiceClient

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        # Create Tables to query
        my_table = table_service_client.create_table(table_name=self.table_name)
        print(my_table)
        # Query tables
        queried_tables = table_service_client.query_tables(filter=self.name_filter, results_per_page=10)
        # table_client.query_tables() returns an itemPaged
        # queried_tables is a list of filtered tables

        for table in queried_tables:
            print(table)
