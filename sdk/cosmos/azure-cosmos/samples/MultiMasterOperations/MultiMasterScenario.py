from Configurations import Configurations
from ConflictWorker import ConflictWorker
from Worker import Worker
from multiprocessing.pool import ThreadPool
import azure.cosmos.documents as documents
from azure.cosmos import CosmosClient

class MultiMasterScenario(object):
    def __init__(self):
        self.account_endpoint = Configurations.ENDPOINT
        self.account_key = Configurations.ACCOUNT_KEY

        self.regions = Configurations.REGIONS.split(';')

        self.database_name = Configurations.DATABASE_NAME
        self.manual_collection_name = Configurations.MANUAL_COLLECTION_NAME
        self.lww_collection_name = Configurations.LWW_COLLECTION_NAME
        self.udp_collection_name = Configurations.UDP_COLLECTION_NAME
        self.basic_collection_name = Configurations.BASIC_COLLECTION_NAME

        self.workers = []
        self.conflict_worker = ConflictWorker(self.database_name, self.basic_collection_name, self.manual_collection_name, self.lww_collection_name, self.udp_collection_name)
        self.pool = ThreadPool(processes = len(self.regions))

        for region in self.regions:
            connection_policy = documents.ConnectionPolicy()
            connection_policy.UseMultipleWriteLocations = True
            connection_policy.PreferredLocations = [region]

            client = CosmosClient(
                url=self.account_endpoint,
                credential=self.account_key,
                consistency_level=documents.ConsistencyLevel.Session,
                connection_policy=connection_policy)

            self.workers.append(Worker(client, self.database_name, self.basic_collection_name))

            self.conflict_worker.add_client(client)

    def initialize_async(self):
        self.conflict_worker.initialize_async()
        print("Initialized collections.")

    def run_basic_async(self):
        print("\n####################################################")
        print("Basic Active-Active")
        print("####################################################")

        print("1) Starting insert loops across multiple regions ...")

        documents_to_insert_per_worker = 100

        run_loop_futures = []
        for worker in self.workers:
            run_loop_future = self.pool.apply_async(worker.run_loop_async, (documents_to_insert_per_worker,))
            run_loop_futures.append(run_loop_future)

        for run_loop_future in run_loop_futures:
            run_loop_future.get()

        print("2) Reading from every region ...")

        expected_documents = len(self.workers) * documents_to_insert_per_worker

        read_all_futures = []
        for worker in self.workers:
            read_all_future = self.pool.apply_async(worker.read_all_async, (expected_documents,))
            read_all_futures.append(read_all_future)

        for read_all_future in read_all_futures:
            read_all_future.get()

        print("3) Deleting all the documents ...")

        self.workers[0].delete_all_async()

        print("####################################################")

    def run_manual_conflict_async(self):
        print("\n####################################################")
        print("Manual Conflict Resolution")
        print("####################################################")

        self.conflict_worker.run_manual_conflict_async()
        print("####################################################")

    def run_LWW_async(self):
        print("\n####################################################")
        print("LWW Conflict Resolution")
        print("####################################################")

        self.conflict_worker.run_LWW_conflict_async()
        print("####################################################")

    def run_UDP_async(self):
        print("\n####################################################")
        print("UDP Conflict Resolution")
        print("####################################################")

        self.conflict_worker.run_UDP_async()
        print("####################################################")
