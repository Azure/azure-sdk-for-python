class CreateODataQuery(object):

    def creating_odata_query_entities(self):

        from azure.storage.tables import TableServiceClient
        from azure.storage.tables._generated.operations._service_operations import HttpResponseError

        table_client = TableServiceClient(account_url=self.account_url, credential=self.account_key)
        try:
            queried_table = table_client.query_table_entities(table_name=self.table_name,partition_key=self.partition_key,row_key=self.row_key)
            print(queried_table.table_name)
        except HttpResponseError as e:
            print(e.message)
