class CreateDeleteTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "OfficeSupplies"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    def shared_key_credential(self):
        from azure.table import TableServiceClient

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)

    def connection_string_auth(self):
        from azure.table import TableServiceClient

        table_service_client = TableServiceClient.from_connection_string(conn_str=self.connection_string)

    def sas_token_auth(self):
        from azure.table import TableServiceClient
        from azure.table._table_shared_access_signature import generate_account_sas
        from azure.table import ResourceTypes
        from azure.table import AccountSasPermissions
        import datetime
        import timedelta

        token = generate_account_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            start=datetime.utcnow() - timedelta(minutes=1),
            )
        table_service_client = TableServiceClient(account_url=self.account_url,credential=token)

    def create_table(self):
        from azure.table import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_created = table_service_client.create_table(table_name=self.table_name)
            print(table_created.table_name)
        except ResourceExistsError:
            print("TableExists")

    def delete_table(self):
        from azure.table import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_service_client.delete_table(table_name=self.table_name)
        except ResourceNotFoundError:
            print("TableNotFound")


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    sample.delete_table()
