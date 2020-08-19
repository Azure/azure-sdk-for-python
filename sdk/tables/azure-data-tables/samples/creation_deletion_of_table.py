import os
import logging

_LOGGER = logging.getLogger(__name__)

class CreateDeleteTable(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")
    table_name = "OfficeSupplies"


    def shared_key_credential(self):
        from azure.data.tables import TableServiceClient

        table_service_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)


    def connection_string_auth(self):
        from azure.data.tables import TableServiceClient

        table_service_client = TableServiceClient.from_connection_string(conn_str=self.connection_string)


    def sas_token_auth(self):
        from azure.data.tables import TableServiceClient
        from azure.data.tables._shared.table_shared_access_signature import generate_account_sas
        from azure.data.tables import ResourceTypes
        from azure.data.tables import AccountSasPermissions
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
        table_service_client = TableServiceClient(account_url=self.account_url, credential=token)


    def create_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_created = table_service_client.create_table(table_name=self.table_name)
            print(table_created.table_name)
        except ResourceExistsError:
            print("Table already exists")


    def delete_table(self):
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceNotFoundError

        table_service_client = TableServiceClient.from_connection_string(self.connection_string)
        try:
            table_service_client.delete_table(table_name=self.table_name)
        except ResourceNotFoundError:
            print("Table coult not be found")


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    sample.delete_table()
