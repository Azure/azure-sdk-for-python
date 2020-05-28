import os


class CreateDeleteTable(object):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    table_name = "NAME"
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

    active_directory_application_id = os.getenv("ACTIVE_DIRECTORY_APPLICATION_ID")
    active_directory_application_secret = os.getenv("ACTIVE_DIRECTORY_APPLICATION_SECRET")
    active_directory_tenant_id = os.getenv("ACTIVE_DIRECTORY_TENANT_ID")

    # functions correctly
    def create_table(self):
        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_created = table_client.create_table(table_name=self.table_name)
            print(table_created.table_name)
            return table_created.table_name
        except HttpResponseError as e:
            print(e.message)

    def delete_table(self):
        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_deleted = table_client.delete_table(table_name=self.table_name)
            print(table_deleted)
            return table_deleted
        except HttpResponseError as e:
            print(e.message)


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    # sample.delete_table()
