class CreateODataQuery(object):

    def creating_odata_query(self):

        from azure.storage.tables import TableServiceClient


        table_client = TableServiceClient(account_url=self.account_url, credential=self.account_key)