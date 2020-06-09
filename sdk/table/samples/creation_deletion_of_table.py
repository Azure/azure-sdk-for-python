import os


class CreateDeleteTable(object):
    connection_string = "DefaultEndpointsProtocol=https;AccountName=example;AccountKey=fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK==;EndpointSuffix=core.windows.net"
    table_name = "NAME"
    account_url = "https://example.table.core.windows.net/"
    account_name = "example"
    access_key = "fasgfbhBDFAShjDQ4jkvbnaBFHJOWS6gkjngdakeKFNLK=="

    # functions correctly
    def create_table(self):
        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceExistsError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)

        try:
            table_created = table_client.create_table(table_name=self.table_name)
            # table_created type is TableResponse
            # Table Response: table_name,odata_type,odata_id,odata_edit_link,odata_metadata
            print(table_created.table_name)
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceExistsError:
            raise ResourceExistsError

    def delete_table(self):
        from azure.azure_table import TableServiceClient
        from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
        table_client = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        try:
            table_deleted = table_client.delete_table(table_name=self.table_name)
            # table_deleted type is None
        except HttpResponseError:
            print(HttpResponseError.response)
        except ResourceNotFoundError:
            raise ResourceNotFoundError


if __name__ == '__main__':
    sample = CreateDeleteTable()
    sample.create_table()
    # sample.delete_table()
