class CreateODataQuery(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="
    partition_key = "1"
    row_key = "1"

    def creating_odata_query_entities(self):

        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError

        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            queried_table = table_client.query_table_entities(table_name=self.table_name,
                                                              partition_key=self.partition_key, row_key=self.row_key)
            print(queried_table.table_name)
        except HttpResponseError as e:
            print(e.message)
