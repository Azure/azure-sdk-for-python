import uuid
import time
from multiprocessing.pool import ThreadPool
import json
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes

class ConflictWorker(object):
    def __init__(self, database_name, basic_collection_name, manual_collection_name, lww_collection_name, udp_collection_name):
        self.clients = []
        self.basic_collection_link = "dbs/" + database_name + "/colls/" + basic_collection_name
        self.manual_collection_link = "dbs/" + database_name + "/colls/" + manual_collection_name
        self.lww_collection_link = "dbs/" + database_name + "/colls/" + lww_collection_name
        self.udp_collection_link = "dbs/" + database_name + "/colls/" + udp_collection_name

        self.database_name = database_name
        self.basic_collection_name = basic_collection_name
        self.manual_collection_name = manual_collection_name
        self.lww_collection_name = lww_collection_name
        self.udp_collection_name = udp_collection_name

    def add_client(self, client):
        self.clients.append(client)

    def initialize_async(self):
        create_client = self.clients[0]
        database = None
        try:
            database = create_client.ReadDatabase("dbs/" + self.database_name)
        except exceptions.CosmosResourceNotFoundError:
            print("database not found, needs to be created.")

        if not database:
            database = {'id': self.database_name}
            database = create_client.CreateDatabase(database)

        basic_collection = {'id': self.basic_collection_name}
        basic = self.try_create_document_collection(create_client, database, basic_collection)

        manual_collection = {
                            'id': self.manual_collection_name,
                            'conflictResolutionPolicy': {
                                 'mode': 'Custom'
                                }
                            }
        manual_collection = self.try_create_document_collection(create_client, database, manual_collection)

        lww_collection = {
                        'id': self.lww_collection_name,
                        'conflictResolutionPolicy': {
                            'mode': 'LastWriterWins',
                            'conflictResolutionPath': '/regionId'
                            }
                        }
        lww_collection = self.try_create_document_collection(create_client, database, lww_collection)

        udp_collection = {
                        'id': self.udp_collection_name,
                        'conflictResolutionPolicy': {
                            'mode': 'Custom',
                            'conflictResolutionProcedure': 'dbs/' + self.database_name + "/colls/" + self.udp_collection_name + '/sprocs/resolver'
                            }
                        }
        udp_collection = self.try_create_document_collection(create_client, database, udp_collection)

        lww_sproc = {'id':'resolver',
                    'body': "function resolver(incomingRecord, existingRecord, isTombstone, conflictingRecords) {\r\n" +
                "    var collection = getContext().getCollection();\r\n" +
                "\r\n" +
                "    if (!incomingRecord) {\r\n" +
                "        if (existingRecord) {\r\n" +
                "\r\n" +
                "            collection.deleteDocument(existingRecord._self, {}, function(err, responseOptions) {\r\n" +
                "                if (err) throw err;\r\n" +
                "            });\r\n" +
                "        }\r\n" +
                "    } else if (isTombstone) {\r\n" +
                "        // delete always wins.\r\n" +
                "    } else {\r\n" +
                "        var documentToUse = incomingRecord;\r\n" +
                "\r\n" +
                "        if (existingRecord) {\r\n" +
                "            if (documentToUse.regionId < existingRecord.regionId) {\r\n" +
                "                documentToUse = existingRecord;\r\n" +
                "            }\r\n" +
                "        }\r\n" +
                "\r\n" +
                "        var i;\r\n" +
                "        for (i = 0; i < conflictingRecords.length; i++) {\r\n" +
                "            if (documentToUse.regionId < conflictingRecords[i].regionId) {\r\n" +
                "                documentToUse = conflictingRecords[i];\r\n" +
                "            }\r\n" +
                "        }\r\n" +
                "\r\n" +
                "        tryDelete(conflictingRecords, incomingRecord, existingRecord, documentToUse);\r\n" +
                "    }\r\n" +
                "\r\n" +
                "    function tryDelete(documents, incoming, existing, documentToInsert) {\r\n" +
                "        if (documents.length > 0) {\r\n" +
                "            collection.deleteDocument(documents[0]._self, {}, function(err, responseOptions) {\r\n" +
                "                if (err) throw err;\r\n" +
                "\r\n" +
                "                documents.shift();\r\n" +
                "                tryDelete(documents, incoming, existing, documentToInsert);\r\n" +
                "            });\r\n" +
                "        } else if (existing) {\r\n" +
                "                collection.replaceDocument(existing._self, documentToInsert,\r\n" +
                "                    function(err, documentCreated) {\r\n" +
                "                        if (err) throw err;\r\n" +
                "                    });\r\n" +
                "        } else {\r\n" +
                "            collection.createDocument(collection.getSelfLink(), documentToInsert,\r\n" +
                "                function(err, documentCreated) {\r\n" +
                "                    if (err) throw err;\r\n" +
                "                });\r\n" +
                "        }\r\n" +
                "    }\r\n" +
                "}"
                }
        try:
            lww_sproc = create_client.CreateStoredProcedure("dbs/" + self.database_name+ "/colls/" + self.udp_collection_name, lww_sproc)
        except exceptions.CosmosResourceExistsError:
            return

    def try_create_document_collection (self, client, database, collection):
        read_collection = None
        try:
            read_collection = client.ReadContainer("dbs/" + database['id'] + "/colls/" + collection['id'])
        except exceptions.CosmosResourceNotFoundError:
            print("collection not found, needs to be created.")

        if read_collection == None:
            collection['partitionKey'] = {'paths': ['/id'],'kind': 'Hash'}
            read_collection = client.CreateContainer(database['_self'], collection)
            print("sleeping for 5 seconds to allow collection create to propagate.")
            time.sleep(5)
        return read_collection

    def run_manual_conflict_async(self):
        print("\r\nInsert Conflict\r\n")
        self.run_insert_conflict_on_manual_async()

        print("\r\nUpdate Conflict\r\n")
        self.run_update_conflict_on_manual_async()

        print("\r\nDelete Conflict\r\n")
        self.run_delete_conflict_on_manual_async()

    def run_LWW_conflict_async(self):
        print("\r\nInsert Conflict\r\n")
        self.run_insert_conflict_on_LWW_async()

        print("\r\nUpdate Conflict\r\n")
        self.run_update_conflict_on_LWW_async()

        print("\r\nDelete Conflict\r\n")
        self.run_delete_conflict_on_LWW_async()

    def run_UDP_async(self):
        print("\r\nInsert Conflict\r\n")
        self.run_insert_conflict_on_UDP_async()

        print("\r\nUpdate Conflict\r\n")
        self.run_update_conflict_on_UDP_async()

        print("\r\nDelete Conflict\r\n")
        self.run_delete_conflict_on_UDP_async()

    def run_insert_conflict_on_manual_async(self):
        while True:
            print("1) Performing conflicting insert across %d regions on %s" % (len(self.clients), self.manual_collection_link))

            id = str(uuid.uuid4())
            i = 0
            pool = ThreadPool(processes = len(self.clients))
            insert_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                insert_document_future = pool.apply_async(self.try_insert_document, (client, self.manual_collection_link, conflict_document))
                insert_document_futures.append(insert_document_future)
                i += 1

            number_of_conflicts = -1
            inserted_documents = []
            for insert_document_future in insert_document_futures:
                inserted_document = insert_document_future.get()
                inserted_documents.append(inserted_document)
                if inserted_document:
                    number_of_conflicts += 1

            if number_of_conflicts > 0:
                print("2) Caused %d insert conflicts, verifying conflict resolution" % number_of_conflicts)

                time.sleep(2) #allow conflicts resolution to propagate
                for conflicting_insert in inserted_documents:
                    if conflicting_insert:
                        self.validate_manual_conflict_async(self.clients, conflicting_insert)
                break
            else:
                print("Retrying insert to induce conflicts")

    def run_update_conflict_on_manual_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.manual_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting update across %d regions on %s" % (len(self.clients), self.manual_collection_link));

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            update_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                update_document_future = pool.apply_async(self.try_update_document, (client, self.manual_collection_link, conflict_document, options))
                update_document_futures.append(update_document_future)
                i += 1

            number_of_conflicts = -1
            update_documents = []
            for update_document_future in update_document_futures:
                update_document = update_document_future.get()
                update_documents.append(update_document)
                if update_document:
                    number_of_conflicts += 1

            if number_of_conflicts > 0:
                print("2) Caused %d update conflicts, verifying conflict resolution" % number_of_conflicts)

                time.sleep(2) #allow conflicts resolution to propagate
                for conflicting_update in update_documents:
                    if conflicting_update:
                        self.validate_manual_conflict_async(self.clients, conflicting_update)
                break
            else:
                print("Retrying update to induce conflicts")

    def run_delete_conflict_on_manual_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.manual_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting delete across %d regions on %s" % (len(self.clients), self.manual_collection_link));

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            delete_document_futures = []
            for client in self.clients:
                conflict_document = conflict_document_for_insertion.copy()
                conflict_document['regionId'] = i
                conflict_document['regionEndpoint'] = client.ReadEndpoint
                delete_document_future = pool.apply_async(self.try_delete_document, (client, self.manual_collection_link, conflict_document, options))
                delete_document_futures.append(delete_document_future)
                i += 1

            number_of_conflicts = -1
            delete_documents = []
            for delete_document_future in delete_document_futures:
                delete_document = delete_document_future.get()
                delete_documents.append(delete_document)
                if delete_document:
                    number_of_conflicts += 1

            if number_of_conflicts > 0:
                print("2) Caused %d delete conflicts, verifying conflict resolution" % number_of_conflicts)

                # Conflicts will not be registered in conflict feed for delete-delete
                # operations. The 'hasDeleteConflict' part of LWW validation can be reused for
                # manual conflict resolution policy validation of delete-delete conflicts.
                self.validate_LWW_async(self.clients, delete_documents, True);
                break
            else:
                print("Retrying delete to induce conflicts")

    def run_insert_conflict_on_LWW_async(self):
        while True:
            print("1) Performing conflicting insert across %d regions on %s" % (len(self.clients), self.lww_collection_link))

            id = str(uuid.uuid4())
            i = 0
            pool = ThreadPool(processes = len(self.clients))
            insert_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                insert_document_future = pool.apply_async(self.try_insert_document, (client, self.lww_collection_link, conflict_document))
                insert_document_futures.append(insert_document_future)
                i += 1

            inserted_documents = []
            for insert_document_future in insert_document_futures:
                inserted_document = insert_document_future.get()
                if inserted_document:
                    inserted_documents.append(inserted_document)

            if len(inserted_documents) > 1:
                print("2) Caused %d insert conflicts, verifying conflict resolution" % len(inserted_documents))
                time.sleep(2) #allow conflicts resolution to propagate
                self.validate_LWW_async(self.clients, inserted_documents, False)
                break
            else:
                print("Retrying insert to induce conflicts")

    def run_update_conflict_on_LWW_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.lww_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting update across %d regions on %s" % (len(self.clients), self.lww_collection_link));

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            update_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                update_document_future = pool.apply_async(self.try_update_document, (client, self.lww_collection_link, conflict_document, options))
                update_document_futures.append(update_document_future)
                i += 1

            update_documents = []
            for update_document_future in update_document_futures:
                update_document = update_document_future.get()
                if update_document:
                    update_documents.append(update_document)

            if len(update_documents) > 1:
                print("2) Caused %d update conflicts, verifying conflict resolution" % len(update_documents))
                time.sleep(2) #allow conflicts resolution to propagate
                self.validate_LWW_async(self.clients, update_documents, False)
                break
            else:
                print("Retrying update to induce conflicts")

    def run_delete_conflict_on_LWW_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.lww_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting update/delete across 3 regions on %s" % self.lww_collection_link)

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            delete_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                delete_document_future = pool.apply_async(self.try_update_or_delete_document, (client, self.lww_collection_link, conflict_document, options))
                delete_document_futures.append(delete_document_future)
                i += 1

            delete_documents = []
            for delete_document_future in delete_document_futures:
                delete_document = delete_document_future.get()
                if delete_document:
                    delete_documents.append(delete_document)

            if len(delete_documents) > 1:
                print("2) Caused %d delete conflicts, verifying conflict resolution" % len(delete_documents))
                time.sleep(2) #allow conflicts resolution to propagate
                # Delete should always win. irrespective of UDP.
                self.validate_LWW_async(self.clients, delete_documents, True)
                break
            else:
                print("Retrying update/delete to induce conflicts")

    def run_insert_conflict_on_UDP_async(self):
        while True:
            print("1) Performing conflicting insert across 3 regions on %s" % self.udp_collection_link)

            id = str(uuid.uuid4())
            i = 0
            pool = ThreadPool(processes = len(self.clients))
            insert_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                insert_document_future = pool.apply_async(self.try_insert_document, (client, self.udp_collection_link, conflict_document))
                insert_document_futures.append(insert_document_future)
                i += 1

            inserted_documents = []
            for insert_document_future in insert_document_futures:
                inserted_document = insert_document_future.get()
                if inserted_document:
                    inserted_documents.append(inserted_document)

            if len(inserted_documents) > 1:
                print("2) Caused %d insert conflicts, verifying conflict resolution" % len(inserted_documents))

                time.sleep(2) #allow conflicts resolution to propagate
                self.validate_UDP_async(self.clients, inserted_documents, False)
                break
            else:
                print("Retrying insert to induce conflicts")

    def run_update_conflict_on_UDP_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.udp_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting update across %d regions on %s" % (len(self.clients), self.udp_collection_link));

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            update_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                update_document_future = pool.apply_async(self.try_update_document, (client, self.udp_collection_link, conflict_document, options))
                update_document_futures.append(update_document_future)
                i += 1

            update_documents = []
            for update_document_future in update_document_futures:
                update_document = update_document_future.get()
                if update_document:
                    update_documents.append(update_document)

            if len(update_documents) > 1:
                print("2) Caused %d update conflicts, verifying conflict resolution" % len(update_documents))

                time.sleep(2) #allow conflicts resolution to propagate
                self.validate_UDP_async(self.clients, update_documents, False)
                break
            else:
                print("Retrying update to induce conflicts")

    def run_delete_conflict_on_UDP_async(self):
        while True:
            id = str(uuid.uuid4())
            conflict_document_for_insertion = {'id': id, 'regionId': 0, 'regionEndpoint': self.clients[0].ReadEndpoint}
            conflict_document_for_insertion = self.try_insert_document(self.clients[0], self.udp_collection_link, conflict_document_for_insertion)
            time.sleep(1) #1 Second for write to sync.

            print("1) Performing conflicting update/delete across 3 regions on %s" % self.udp_collection_link)

            i = 0
            options = {'accessCondition': {'condition': 'IfMatch', 'type': conflict_document_for_insertion['_etag']}}
            pool = ThreadPool(processes = len(self.clients))
            delete_document_futures = []
            for client in self.clients:
                conflict_document = {'id': id, 'regionId': i, 'regionEndpoint': client.ReadEndpoint}
                delete_document_future = pool.apply_async(self.try_update_or_delete_document, (client, self.udp_collection_link, conflict_document, options))
                delete_document_futures.append(delete_document_future)
                i += 1

            delete_documents = []
            for delete_document_future in delete_document_futures:
                delete_document = delete_document_future.get()
                if delete_document:
                    delete_documents.append(delete_document)

            if len(delete_documents) > 1:
                print("2) Caused %d delete conflicts, verifying conflict resolution" % len(delete_documents))

                time.sleep(2) #allow conflicts resolution to propagate
                # Delete should always win. irrespective of UDP.
                self.validate_UDP_async(self.clients, delete_documents, True)
                break
            else:
                print("Retrying update/delete to induce conflicts")

    def try_insert_document(self, client, collection_uri, document):
        try:
            return client.CreateItem(collection_uri, document)
        except exceptions.CosmosResourceExistsError:
            return None

    def try_update_document(self, client, collection_uri, document, options):
        try:
            options['partitionKey'] = document['id']
            return client.ReplaceItem(collection_uri + "/docs/" + document['id'], document, options);
        except (exceptions.CosmosResourceNotFoundError, exceptions.CosmosAccessConditionFailedError):
            # Lost synchronously or no document yet. No conflict is induced.
            return None

    def try_delete_document(self, client, collection_uri, document, options):
        try:
            options['partitionKey'] = document['id']
            client.DeleteItem(collection_uri + "/docs/" + document['id'], options)
            return document
        except (exceptions.CosmosResourceNotFoundError, exceptions.CosmosAccessConditionFailedError):
            #Lost synchronously. No conflict is induced.
            return None

    def try_update_or_delete_document(self, client, collection_uri, conflict_document, options):
        if int(conflict_document['regionId']) % 2 == 1:
            #We delete from region 1, even though region 2 always win.
            return self.try_delete_document(client, collection_uri, conflict_document, options)
        else:
            return self.try_update_document(client, collection_uri, conflict_document, options)

    def validate_manual_conflict_async(self, clients, conflict_document):

        conflict_exists = False
        for client in clients:
            conflict_exists = self.validate_manual_conflict_async_internal(client, conflict_document)

        if conflict_exists:
            self.delete_conflict_async(conflict_document)

    def validate_manual_conflict_async_internal(self, client, conflict_document):
        while True:
            conflicts_iterartor = iter(client.ReadConflicts(self.manual_collection_link))
            conflict = next(conflicts_iterartor, None)
            while conflict:
                if conflict['operationType'] != 'delete':
                    conflict_document_content = json.loads(conflict['content'])

                    if conflict_document['id'] == conflict_document_content['id']:
                        if ((conflict_document['_rid'] == conflict_document_content['_rid']) and
                            (conflict_document['_etag'] == conflict_document_content['_etag'])):
                            print("Document from Region %d lost conflict @ %s" %
                                  (int(conflict_document['regionId']), client.ReadEndpoint))
                            return True
                        else:
                            #Checking whether this is the winner.
                            options = {'partitionKey': conflict_document['id']}
                            winner_document = client.ReadItem(conflict_document['_self'], options)
                            print("Document from Region %d won the conflict @ %s" %
                                  (int(winner_document['regionId']), client.ReadEndpoint))
                            return False
                else:
                    if conflict['resourceId'] == conflict_document['_rid']:
                        print("Delete conflict found @ %s" % client.ReadEndpoint)
                        return False
                conflict = next(conflicts_iterartor, None)

            self.trace_error("Document %s is not found in conflict feed @ %s, retrying" %
                             (conflict_document['id'], client.ReadEndpoint))

            time.sleep(0.5)

    def delete_conflict_async(self, conflict_document):
        del_client = self.clients[0]
        conflicts_iterartor = iter(del_client.ReadConflicts(self.manual_collection_link))
        conflict = next(conflicts_iterartor, None)

        while conflict:
            conflict_content = json.loads(conflict['content'])
            options = {'partitionKey': conflict_content['id']}

            if conflict['operationType'] != 'delete':
                if ((conflict_content['_rid'] == conflict_document['_rid']) and
                    (conflict_content['_etag'] == conflict_document['_etag'])):
                    print("Deleting manual conflict %s from region %d" %
                          (conflict['resourceId'],
                           int(conflict_content['regionId'])))
                    del_client.DeleteConflict(conflict['_self'], options)
            elif conflict['resourceId'] == conflict_document['_rid']:
                print("Deleting manual conflict %s from region %d" %
                      (conflict['resourceId'],
                       int(conflict_document['regionId'])))
                del_client.DeleteConflict(conflict['_self'], options)
            conflict = next(conflicts_iterartor, None)

    def validate_LWW_async(self, clients, conflict_document, has_delete_conflict):
        for client in clients:
            self.validate_LWW_async_internal(client, conflict_document, has_delete_conflict)

    def validate_LWW_async_internal(self, client, conflict_document, has_delete_conflict):
        conflicts_iterartor =iter(client.ReadConflicts(self.lww_collection_link))

        conflict = next(conflicts_iterartor, None)
        conflict_count = 0
        while conflict:
            conflict_count += 1
            conflict = next(conflicts_iterartor, None)

        if conflict_count > 0:
            self.trace_error("Found %d conflicts in the lww collection" % conflict_count)
            return

        if has_delete_conflict:
            while True:
                try:
                    options = {'partitionKey': conflict_document[0]['id']}
                    client.ReadItem(conflict_document[0]['_self'], options)

                    self.trace_error("Delete conflict for document %s didnt win @ %s" %
                                     (conflict_document[0]['id'], client.ReadEndpoint))

                    time.sleep(0.5)
                except exceptions.CosmosResourceNotFoundError:
                    print("Delete conflict won @ %s" % client.ReadEndpoint)
                    return
                except exceptions.CosmosHttpResponseError:
                    self.trace_error("Delete conflict for document %s didnt win @ %s" %
                                    (conflict_document[0]['id'], client.ReadEndpoint))

                    time.sleep(0.5)

        winner_document = None

        for document in conflict_document:
            if winner_document is None or int(winner_document['regionId']) <= int(document['regionId']):
                winner_document = document

        print("Document from region %d should be the winner" % int(winner_document['regionId']))

        while True:
            try:
                options = {'partitionKey': winner_document['id']}
                existing_document = client.ReadItem(winner_document['_self'], options)

                if int(existing_document['regionId']) == int(winner_document['regionId']):
                    print("Winner document from region %d found at %s" %
                          (int(existing_document['regionId']), client.ReadEndpoint))
                    break
                else:
                    self.trace_error("Winning document version from region %d is not found @ %s, retrying..." %
                                     (int(winner_document["regionId"]), client.WriteEndpoint))

                    time.sleep(0.5)
            except exceptions.AzureError as e:
                self.trace_error("Winner document from region %d is not found @ %s, retrying..." %
                                (int(winner_document["regionId"]), client.WriteEndpoint))

                time.sleep(0.5)

    def validate_UDP_async(self, clients, conflict_document, has_delete_conflict):
        for client in clients:
            self.validate_UDP_async_internal(client, conflict_document, has_delete_conflict)

    def validate_UDP_async_internal(self, client, conflict_document, has_delete_conflict):
        conflicts_iterartor = iter(client.ReadConflicts(self.udp_collection_link))

        conflict = next(conflicts_iterartor, None)
        conflict_count = 0
        while conflict:
            conflict_count += 1
            conflict = next(conflicts_iterartor, None)

        if conflict_count > 0:
            self.trace_error("Found %d conflicts in the udp collection" % conflictCount)
            return

        if has_delete_conflict:
            while True:
                try:
                    options = {'partitionKey': conflict_document[0]['id']}
                    client.ReadItem(conflict_document[0]['_self'], options)

                    self.trace_error("Delete conflict for document %s didnt win @ %s" %
                                     (conflict_document[0]['id'], client.ReadEndpoint))

                    time.sleep(0.5)
                except exceptions.CosmosResourceNotFoundError:
                    print("Delete conflict won @ %s" % client.ReadEndpoint)
                    return
                except exceptions.CosmosHttpResponseError:
                    self.trace_error("Delete conflict for document %s didnt win @ %s" %
                                    (conflict_document[0]['id'], client.ReadEndpoint))
                    time.sleep(0.5)

        winner_document = None

        for document in conflict_document:
            if winner_document is None or int(winner_document['regionId']) <= int(document['regionId']):
                winner_document = document;

        print("Document from region %d should be the winner" % int(winner_document['regionId']))

        while True:
            try:
                options = {'partitionKey': winner_document['id']}
                existing_document = client.ReadItem(self.udp_collection_link + "/docs/" + winner_document['id'], options)

                if int(existing_document['regionId']) == int(winner_document['regionId']):
                    print("Winner document from region %d found at %s" %
                          (int(existing_document["regionId"]), client.ReadEndpoint))
                    break
                else:
                    self.trace_error("Winning document version from region %d is not found @ %s, retrying..." %
                                     (int(winner_document['regionId']), client.WriteEndpoint))

                    time.sleep(0.5)
            except exceptions.AzureError:
                self.trace_error("Winner document from region %d is not found @ %s, retrying..." %
                                 (int(winner_document['regionId']), client.WriteEndpoint))
                time.sleep(0.5)

    def trace_error(self, message):
        print('\n' + message + '\n')
