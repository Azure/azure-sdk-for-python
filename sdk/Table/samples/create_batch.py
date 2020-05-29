class CreateBatch(object):
    def build_batch_operations(self):
        from azure.storage.tables import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url,credential=self.credential)
        batch_operations = table_client.batch(*self.reqs)
