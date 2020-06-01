class QueryTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    def queryTable(self):
        from azure.azure_table import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        queried_table = table_client.query_table(table_name=self.table_name)
        print(queried_table.table_name)


if __name__ == '__main__':
    sample = QueryTable()
    sample.queryTable()
