import uuid
import time
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes

class Worker(object):
    def __init__(self, client, database_name, collection_name):
        self.client = client
        self.database = client.get_database_client(database_name)
        self.document_collection = self.database.get_container_client(collection_name)
        self.document_collection_link = "dbs/" + database_name + "/colls/" + collection_name

    def run_loop_async(self, documents_to_insert):
        iteration_count = 0

        latency = []
        while iteration_count < documents_to_insert:
            document = {'id':  str(uuid.uuid4())}
            iteration_count += 1

            start = int(round(time.time() * 1000))
            self.document_collection.create_item(document)
            end = int(round(time.time() * 1000))

            latency.append(end - start)

        latency = sorted(latency)
        p50_index = int(len(latency) / 2)

        print("Inserted %d documents at %s with p50 %d ms" %
            (documents_to_insert,
            self.client.client_connection.WriteEndpoint,
            latency[p50_index]))

    def read_all_async(self, expected_number_of_documents):
        while True:
            total_item_read = 0
            # query_iterable = self.document_collection.ReadItems(self.document_collection_link)
            query_iterable = self.document_collection.read_all_items()
            it = iter(query_iterable)

            doc = next(it, None)
            while doc:
                total_item_read += 1
                doc = next(it, None)

            if total_item_read < expected_number_of_documents:
                print("Total item read %d from %s is less than %d, retrying reads" %
                        (total_item_read,
                        self.client.client_connection.WriteEndpoint,
                        expected_number_of_documents))
                time.sleep(1)
                continue
            else:
                print("Read %d items from %s" % (total_item_read, self.client.client_connection.ReadEndpoint))
                break


    def delete_all_async(self):
        query_iterable = self.document_collection.read_all_items()
        it = iter(query_iterable)

        doc = next(it, None)
        while doc:
            try:
                self.document_collection.delete_item(item=doc['id'], partition_key=doc['id'])
            except exceptions.CosmosResourceNotFoundError:
                raise
            except exceptions.CosmosHttpResponseError as e:
                print("Error occurred while deleting document from %s" % self.client.client_connection.WriteEndpoint)

            doc = next(it, None)
        print("Deleted all documents from region %s" % self.client.client_connection.WriteEndpoint)