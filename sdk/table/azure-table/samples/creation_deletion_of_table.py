class CreateDeleteTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "OfficeSupplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

# Table Service Client the rest are table level so no table name
    def shared_key_credential(self):
        from azure.table import TableServiceClient

        table_service = TableServiceClient(account_url=self.account_url, credential=self.access_key)

    def create_table(self):
        from azure.table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceExistsError

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)

        try:
            table_created = table_service_client.create_table(table_name=self.table_name)
            print(table_created.table_name)
        except ResourceExistsError:
            raise ResourceExistsError

    def delete_table(self):
        from azure.table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_deleted = table_service_client.delete_table(table_name=self.table_name)
            # table_deleted type is None
        except ResourceNotFoundError:
            raise ResourceNotFoundError


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    # sample.delete_table()
