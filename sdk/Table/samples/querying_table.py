class QueryTable(object):

    def queryTable(self):
        from azure.storage.tables import TableServiceClient
        table_client = TableServiceClient(account_url=self.account_url, credential=self.credential)
        queried_table = table_client.query_table_entities(table_name=self.table_name)
        print(queried_table.table_name)


if __name__ == '__main__':
    sample = QueryTable()
    sample.queryTable()
