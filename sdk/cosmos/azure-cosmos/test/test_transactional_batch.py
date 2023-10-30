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

        # empty batch
        try:
            container.execute_item_batch(batch_operations=[], partition_key="Microsoft")
            pytest.fail("Operation should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Batch request has no operations." in e.message

        # batch with > 100 items
        batch = []
        for i in range(101):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))
        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Operation should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Batch request has more operations than what is supported." in e.message

        # batch too large
        item_id = str(uuid.uuid4())
        massive_item = {"id": item_id, "company": "Microsoft"}
        while len(str(massive_item)) < 2500000:
            for i in range(100):
                massive_item.update({str(uuid.uuid4()): str(uuid.uuid4())})
        batch = [("create", (massive_item,))]
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
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 100

        # create the same item twice
        item_id = str(uuid.uuid4())
        batch = [("create", ({"id": item_id, "company": "Microsoft"},)),
                 ("create", ({"id": item_id, "company": "Microsoft"},))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.CONFLICT
            assert e.error_index == 1
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            assert operation_results[1].get("statusCode") == StatusCodes.CONFLICT

        # create an item without the right partition key.
        batch = [("create", ({"id": str(uuid.uuid4()), "company": "Microsoft"},)),
                 ("create", ({"id": str(uuid.uuid4()), "company": "Not-Microsoft"},))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert e.error_index == 1
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            assert operation_results[1].get("statusCode") == StatusCodes.BAD_REQUEST

        # create an item without a partition key
        batch = [("create", ({"id": str(uuid.uuid4()), "company": "Microsoft"},)),
                 ("create", ({"id": str(uuid.uuid4()), "name": "Simon"},))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert e.error_index == 1
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            assert operation_results[1].get("statusCode") == StatusCodes.BAD_REQUEST

    def test_batch_read(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_read" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        batch = []
        for i in range(100):
            container.create_item({"id": "item" + str(i), "company": "Microsoft"})
            batch.append(("read", ("item" + str(i),)))

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 100
        for result in batch_response:
            assert result.get("statusCode") == 200

        # read non-existent item
        batch = [("read", (str(uuid.uuid4()),)),
                 ("read", (str(uuid.uuid4()),))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.NOT_FOUND
            assert e.error_index == 0
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.NOT_FOUND
            assert operation_results[1].get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_replace(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_replace" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        batch = [("create", ({"id": "new-item", "company": "Microsoft"},)),
                 ("replace", ("new-item", {"id": "new-item", "company": "Microsoft", "message": "item was replaced"}))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 2
        assert batch_response[1].get("resourceBody").get("message") == "item was replaced"

        # replace non-existent
        batch = [("replace", ("no-item", {"id": "no-item", "company": "Microsoft", "message": "item was replaced"}))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.NOT_FOUND
            assert e.error_index == 0
            operation_results = e.operation_responses
            assert len(operation_results) == 1
            assert operation_results[0].get("statusCode") == StatusCodes.NOT_FOUND

        # replace with wrong etag
        item_id = str(uuid.uuid4())
        batch = [("upsert", ({"id": item_id, "company": "Microsoft"},)),
                 ("replace", (item_id, {"id": item_id, "company": "Microsoft", "message": "item was replaced"}),
                  {"if_match_etag": "some-tag"}),
                 ("replace", (item_id, {"id": item_id, "company": "Microsoft", "message": "item was replaced"}),
                  {"if_none_match_etag": "some-tag"})]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.PRECONDITION_FAILED
            assert e.error_index == 1
            operation_results = e.operation_responses
            assert len(operation_results) == 3
            assert operation_results[0].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            assert operation_results[1].get("statusCode") == StatusCodes.PRECONDITION_FAILED
            assert operation_results[2].get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_upsert(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_upsert" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        item_id = str(uuid.uuid4())
        batch = [("upsert", ({"id": item_id, "company": "Microsoft"},)),
                 ("upsert", ({"id": item_id, "company": "Microsoft", "message": "item was upsert"},)),
                 ("upsert", ({"id": str(uuid.uuid4()), "company": "Microsoft"},))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 3
        assert batch_response[1].get("resourceBody").get("message") == "item was upsert"

    def test_batch_patch(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_patch" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        item_id = str(uuid.uuid4())
        batch = [("upsert", ({"id": item_id,
                              "company": "Microsoft",
                              "city": "Seattle",
                              "port": 9000,
                              "remove_path": True,
                              "move_path": "yes",
                              "set_path": 1},)),
                 ("patch", (item_id, [
                     {"op": "add", "path": "/favorite_color", "value": "red"},
                     {"op": "remove", "path": "/remove_path"},
                     {"op": "replace", "path": "/city", "value": "Redmond"},
                     {"op": "set", "path": "/set_path", "value": 0},
                     {"op": "incr", "path": "/port", "value": 5},
                     {"op": "move", "from": "/move_path", "path": "/moved_path"}]))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 2
        assert batch_response[1].get("resourceBody").get("favorite_color") == "red"
        assert batch_response[1].get("resourceBody").get("remove_path") is None
        assert batch_response[1].get("resourceBody").get("city") == "Redmond"
        assert batch_response[1].get("resourceBody").get("set_path") == 0
        assert batch_response[1].get("resourceBody").get("port") == 9005
        assert batch_response[1].get("resourceBody").get("move_path") is None
        assert batch_response[1].get("resourceBody").get("moved_path") == "yes"

        # conditional patching incorrect filter
        item_id = str(uuid.uuid4())
        batch = [("upsert", ({"id": item_id,
                              "company": "Microsoft",
                              "city": "Seattle",
                              "port": 9000,
                              "remove_path": True,
                              "move_path": "yes",
                              "set_path": 1},)),
                 ("patch", (item_id, [{"op": "add", "path": "/favorite_color", "value": "red"}]),
                  {"filter_predicate": "from c where c.set_path = 0"})]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.PRECONDITION_FAILED
            assert e.error_index == 1
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.FAILED_DEPENDENCY
            assert operation_results[1].get("statusCode") == StatusCodes.PRECONDITION_FAILED

        # with correct filter
        batch = [("upsert", ({"id": item_id,
                              "company": "Microsoft",
                              "city": "Seattle",
                              "port": 9000,
                              "remove_path": True,
                              "move_path": "yes",
                              "set_path": 1},)),
                 ("patch", (item_id, [{"op": "add", "path": "/favorite_color", "value": "red"}]),
                  {"filter_predicate": "from c where c.set_path = 1"})]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 2

    def test_batch_delete(self):
        self._set_up()
        container = self.test_database.create_container_if_not_exists(id="batch_delete" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        create_batch = []
        delete_batch = []
        for i in range(10):
            item_id = str(uuid.uuid4())
            create_batch.append(("create", ({"id": item_id, "company": "Microsoft"},)))
            delete_batch.append(("delete", (item_id,)))

        batch_response = container.execute_item_batch(batch_operations=create_batch, partition_key="Microsoft")
        assert len(batch_response) == 10
        assert len(list(container.read_all_items())) == 10

        batch_response = container.execute_item_batch(batch_operations=delete_batch, partition_key="Microsoft")
        assert len(batch_response) == 10
        assert len(list(container.read_all_items())) == 0

        # delete non-existent item
        batch = [("delete", ("new-item",)),
                 ("delete", ("new-item",))]

        try:
            container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
            pytest.fail("Request should have failed.")
        except exceptions.CosmosBatchOperationError as e:
            assert e.status_code == StatusCodes.NOT_FOUND
            assert e.error_index == 0
            operation_results = e.operation_responses
            assert len(operation_results) == 2
            assert operation_results[0].get("statusCode") == StatusCodes.NOT_FOUND
            assert operation_results[1].get("statusCode") == StatusCodes.FAILED_DEPENDENCY

    def test_batch_lsn(self):
        container = self.test_database.create_container_if_not_exists(id="batch_lsn" + str(uuid.uuid4()),
                                                                      partition_key=PartitionKey(path="/company"))
        # create test items
        container.upsert_item({"id": "read_item", "company": "Microsoft"})
        container.upsert_item({"id": "replace_item", "company": "Microsoft", "value": 0})
        container.upsert_item({"id": "patch_item", "company": "Microsoft"})
        container.upsert_item({"id": "delete_item", "company": "Microsoft"})

        container.read_item(item="read_item", partition_key="Microsoft")
        lsn = container.client_connection.last_response_headers.get(HttpHeaders.LSN)

        batch = [("create", ({"id": "create_item", "company": "Microsoft"},)),
                 ("replace", ("replace_item", {"id": "replace_item", "company": "Microsoft", "value": True})),
                 ("upsert", ({"id": "upsert_item", "company": "Microsoft"},)),
                 ("patch", ("patch_item", [{"op": "add", "path": "/favorite_color", "value": "red"}])),
                 ("read", ("read_item",)),
                 ("delete", ("delete_item",))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response) == 6
        assert int(lsn) == int(container.client_connection.last_response_headers.get(HttpHeaders.LSN)) - 1

    def test_batch_subpartition(self):
        container = self.test_database.create_container_if_not_exists(
            id="batch_subpartition" + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/state", "/city", "/zipcode"], kind="MultiHash"))
        item_ids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        container.upsert_item({'id': item_ids[0],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[1],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})
        container.upsert_item({'id': item_ids[2],
                               'key': 'value',
                               'state': 'WA',
                               'city': 'Redmond',
                               'zipcode': '98052'})

        batch = [("create", (get_subpartition_item(str(uuid.uuid4())),)),
                 ("replace", (item_ids[0], {"id": item_ids[0],
                                            'state': 'WA',
                                            'city': 'Redmond',
                                            'zipcode': '98052',
                                            'replaced': True})),
                 ("upsert", (get_subpartition_item(str(uuid.uuid4())),)),
                 ("patch", (item_ids[1], [{"op": "add", "path": "/favorite_color", "value": "red"}])),
                 ("read", (item_ids[2],)),
                 ("delete", (item_ids[2],))]

        batch_response = container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond", "98052"])
        assert len(batch_response) == 6

        # try to use incomplete key
        try:
            container.execute_item_batch(batch_operations=batch, partition_key=["WA", "Redmond"])
            pytest.fail("Request should have failed.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
            assert "Partition key provided either doesn't correspond to " \
                   "definition in the collection or doesn't match partition key " \
                   "field values specified in the document." in e.message
