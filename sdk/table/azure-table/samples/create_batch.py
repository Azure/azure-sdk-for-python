class CreateBatch(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # demonstrate building a batch of operations and commit that batch

    def build_batch_operations(self):
        from azure.azure_table import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        batch_operations = table_client.batch(*self.reqs)
