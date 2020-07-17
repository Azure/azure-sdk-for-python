class TableErrorHandling:
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "OfficeSupplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    def create_table_if_exists(self):
        from azure.table import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        # create table
        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        table_service_client.create_table(table_name=self.table_name)
        try:
            # try to create existing table, ResourceExistsError will be thrown
            table_service_client.create_table(table_name=self.table_name)
        except ResourceExistsError:
            print("TableExists")


if __name__ == '__main__':
    sample = TableErrorHandling()
    sample.create_table_if_exists()