# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid
import pytest
import test_config

from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos.http_constants import HttpHeaders, StatusCodes

pytestmark = pytest.mark.cosmosEmulator


def get_subpartition_item(item_id):
    return {'id': item_id,
            'key': 'value',
            'state': 'WA',
            'city': 'Redmond',
            'zipcode': '98052'}


@pytest.mark.usefixtures("teardown")
class TestTransactionalBatch:
    """Python Transactional Batch Tests.
    """

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey

    @classmethod
    def _set_up(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.test_database = cls.client.create_database_if_not_exists(cls.configs.TEST_DATABASE_ID)

    def test_invalid_batch_sizes(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="invalid_batch_size" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))

        # Empty batch
        try:
            container.execute_item_batch(batch_operations=[], partition_key="Microsoft")
            pytest.fail("Operation should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Batch request has no operations." in e.message

        # Batch with > 100 items
        batch = []
        for i in range(101):
            batch.append({"operationType": "Create",
                          "resourceBody": {"id": "item" + str(i)}, "company": "Microsoft"})
        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Operation should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Batch request has more operations than what is supported." in e.message

        # Batch too large
        item_id = str(uuid.uuid4())
        massive_item = {"id": item_id, "company": "Microsoft"}
        while len(str(massive_item)) < 2500000:
            for i in range(100):
                massive_item.update({str(uuid.uuid4()): str(uuid.uuid4())})
        batch = [{"operationType": "Create",
                  "resourceBody": massive_item}]
        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("test should have failed")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.REQUEST_ENTITY_TOO_LARGE
            assert e.message.startswith("(RequestEntityTooLarge)")

    def test_batch_create(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_create" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        batch = []
        for i in range(100):
            batch.append({"operationType": "Create",
                          "resourceBody": {"id": "item" + str(i), "company": "Microsoft"}})
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        assert len(batch_response.get("results")) == 100

        # Create the same item twice
        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Create",
                  "resourceBody": {"id": item_id, "company": "Microsoft"}},
                 {"operationType": "Create",
                  "resourceBody": {"id": item_id, "company": "Microsoft"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is True
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.CONFLICT

        # Create an item without the right partition key.
        batch = [{"operationType": "Create",
                  "resourceBody": {"id": str(uuid.uuid4()), "company": "Microsoft"}},
                 {"operationType": "Create",
                  "resourceBody": {"id": str(uuid.uuid4()), "company": "Not-Microsoft"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is True
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.BAD_REQUEST

        # Create an item without a partition key
        batch = [{"operationType": "Create",
                  "resourceBody": {"id": str(uuid.uuid4()), "company": "Microsoft"}},
                 {"operationType": "Create",
                  "resourceBody": {"id": str(uuid.uuid4()), "name": "Simon"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is True
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.BAD_REQUEST

    def test_batch_read(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_read" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        batch = []
        for i in range(100):
            container.create_item({"id": "item" + str(i), "company": "Microsoft"})
            batch.append({"operationType": "Read",
                          "id": "item" + str(i)})
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 100
        for result in operation_results:
            result = result.operation_response
            assert result.get("statusCode") == 200

        # Read non-existent item
        batch = [{"operationType": "Read",
                  "id": str(uuid.uuid4())},
                 {"operationType": "Read",
                  "id": str(uuid.uuid4())}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is True
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.NOT_FOUND
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_replace(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_replace" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Create",
                  "resourceBody": {"id": item_id, "company": "Microsoft"}},
                 {"operationType": "Replace",
                  "id": item_id,
                  "resourceBody": {"id": item_id, "company": "Microsoft", "message": "item was replaced"}}]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[1].operation_response.get("resourceBody").get("message") == "item was replaced"

        # Replace non-existent
        batch = [{"operationType": "Replace",
                  "id": "new-item",
                  "resourceBody": {"id": "new-item", "company": "Microsoft", "message": "item was replaced"}}]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error")
        operation_results = batch_response.get("results")
        assert len(operation_results) == 1
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.NOT_FOUND

        # Replace with wrong etag
        container.read()
        etag = container.client_connection.last_response_headers.get('etag')

        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Create",
                  "resourceBody": {"id": item_id, "company": "Microsoft"}},
                 {"operationType": "Replace",
                  "id": item_id,
                  "resourceBody": {"id": item_id, "company": "Microsoft", "message": "item was replaced"},
                  "ifMatch": etag},
                 {"operationType": "Replace",
                  "id": item_id,
                  "resourceBody": {"id": item_id, "company": "Microsoft", "message": "item was replaced"},
                  "ifNoneMatch": etag}]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error")
        operation_results = batch_response.get("results")
        assert len(operation_results) == 3
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.PRECONDITION_FAILED
        assert operation_results[2].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_upsert(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_upsert" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Upsert",
                  "resourceBody": {"id": item_id, "company": "Microsoft"}},
                 {"operationType": "Upsert",
                  "resourceBody": {"id": item_id, "company": "Microsoft", "message": "item was upsert"}},
                 {"operationType": "Upsert",
                  "resourceBody": {"id": str(uuid.uuid4()), "company": "Microsoft"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 3
        assert operation_results[1].operation_response.get("resourceBody").get("message") == "item was upsert"

    def test_batch_patch(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_patch" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Upsert",
                  "resourceBody": {"id": item_id,
                                   "company": "Microsoft",
                                   "city": "Seattle",
                                   "port": 9000,
                                   "remove_path": True,
                                   "move_path": "yes",
                                   "set_path": 1}},
                 {"operationType": "Patch",
                  "id": item_id,
                  "resourceBody": {"operations": [
                      {"op": "add", "path": "/favorite_color", "value": "red"},
                      {"op": "remove", "path": "/remove_path"},
                      {"op": "replace", "path": "/city", "value": "Redmond"},
                      {"op": "set", "path": "/set_path", "value": 0},
                      {"op": "incr", "path": "/port", "value": 5},
                      {"op": "move", "from": "/move_path", "path": "/moved_path"}]}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[1].operation_response.get("resourceBody").get("favorite_color") == "red"
        assert operation_results[1].operation_response.get("resourceBody").get("remove_path") is None
        assert operation_results[1].operation_response.get("resourceBody").get("city") == "Redmond"
        assert operation_results[1].operation_response.get("resourceBody").get("set_path") == 0
        assert operation_results[1].operation_response.get("resourceBody").get("port") == 9005
        assert operation_results[1].operation_response.get("resourceBody").get("move_path") is None
        assert operation_results[1].operation_response.get("resourceBody").get("moved_path") == "yes"

        # With conditional patching
        item_id = str(uuid.uuid4())
        batch = [{"operationType": "Upsert",
                  "resourceBody": {"id": item_id,
                                   "company": "Microsoft",
                                   "city": "Seattle",
                                   "port": 9000,
                                   "remove_path": True,
                                   "move_path": "yes",
                                   "set_path": 1}},
                 {"operationType": "Patch",
                  "id": item_id,
                  "resourceBody": {"operations": [{"op": "add", "path": "/favorite_color", "value": "red"}],
                                   "condition": "from c where c.set_path = 0"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error")
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.PRECONDITION_FAILED

        # With correct filter
        batch = [{"operationType": "Upsert",
                  "resourceBody": {"id": item_id,
                                   "company": "Microsoft",
                                   "city": "Seattle",
                                   "port": 9000,
                                   "remove_path": True,
                                   "move_path": "yes",
                                   "set_path": 1}},
                 {"operationType": "Patch",
                  "id": item_id,
                  "resourceBody": {"operations": [{"op": "add", "path": "/favorite_color", "value": "red"}],
                                   "condition": "from c where c.set_path = 1"}}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2

    def test_batch_delete(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_delete" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        create_batch = []
        delete_batch = []
        for i in range(10):
            item_id = str(uuid.uuid4())
            create_batch.append({"operationType": "Create",
                                 "resourceBody": {"id": item_id, "company": "Microsoft"}})
            delete_batch.append({"operationType": "Delete",
                                 "id": item_id})

        batch_response = container.execute_item_batch(batch_operations=create_batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 10
        assert len(list(container.read_all_items())) == 10

        batch_response = container.execute_item_batch(batch_operations=delete_batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 10
        assert len(list(container.read_all_items())) == 0

        # Delete non-existent item
        batch = [{"operationType": "Delete",
                  "id": "new-item"},
                 {"operationType": "Delete",
                  "id": "new-item"}]
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is True
        operation_results = batch_response.get("results")
        assert len(operation_results) == 2
        assert operation_results[0].operation_response.get("statusCode") == StatusCodes.NOT_FOUND
        assert operation_results[1].operation_response.get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_lsn(self):
        container = self.test_database.create_container_if_not_exists(id="batch_lsn" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        # Create test items
        container.upsert_item({"id": "read_item", "company": "Microsoft"})
        container.upsert_item({"id": "replace_item", "company": "Microsoft", "value": 0})
        container.upsert_item({"id": "patch_item", "company": "Microsoft"})
        container.upsert_item({"id": "delete_item", "company": "Microsoft"})

        container.read_item(item="read_item", partition_key="Microsoft")
        lsn = container.client_connection.last_response_headers.get(HttpHeaders.LSN)

        batch = []
        batch.append({"operationType": "Create",
                      "resourceBody": {"id": "create_item", "company": "Microsoft"}})
        batch.append({"operationType": "Replace",
                      "id": "replace_item",
                      "resourceBody": {"id": "replace_item", "company": "Microsoft", "value": True}})
        batch.append({"operationType": "Upsert",
                      "resourceBody": {"id": "upsert_item", "company": "Microsoft"}})
        batch.append({"operationType": "Patch",
                      "id": "patch_item",
                      "resourceBody": {"operations": [
                          {"op": "add", "path": "/favorite_color", "value": "red"}]}})
        batch.append({"operationType": "Read",
                      "id": "read_item"})
        batch.append({"operationType": "Delete",
                      "id": "delete_item"})

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 6
        assert int(lsn) == int(container.client_connection.last_response_headers.get(HttpHeaders.LSN)) - 1

    def test_batch_subpartition(self):
        container = self.test_database.create_container_if_not_exists(
            id="batch_subpartition" + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"))
        item_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        container.upsert_item({'id': item_ids[0], 'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[1], 'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[2],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        batch = []
        batch.append({"operationType": "Create",
                      "resourceBody": get_subpartition_item(str(uuid.uuid4()))})
        batch.append({"operationType": "Replace",
                      "id": item_ids[0],
                      "resourceBody": {"id": item_ids[0],
                                       'state': 'WA',
                                       'city': 'Redmond',
                                       'zipcode': '98052',
                                       'replaced': True}})
        batch.append({"operationType": "Upsert",
                      "resourceBody": get_subpartition_item(str(uuid.uuid4()))})
        batch.append({"operationType": "Patch",
                      "id": item_ids[1],
                      "resourceBody": {"operations": [
                          {"op": "add", "path": "/favorite_color", "value": "red"}]}})
        batch.append({"operationType": "Read",
                      "id": item_ids[2]})
        batch.append({"operationType": "Delete",
                      "id": item_ids[2]})

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond", "98052"])
        assert batch_response.get("is_error") is False
        operation_results = batch_response.get("results")
        assert len(operation_results) == 6

        # Try to use incomplete key
        try:
            container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond"])
            pytest.fail("Request should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to " \
                   "definition in the collection or doesn't match partition key " \
                   "field values specified in the document." in e.message
