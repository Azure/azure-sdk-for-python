# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged legacy policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
import time
from azure.cosmos import CosmosClient
from replace_container._legacy_setup import SyncReplacementCase

class TestComputedPropertiesQuery(SyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    def _initialize_data(self):
        self.items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'prefixOne', 'db_group': 'GroUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'prefixTwo', 'db_group': 'GrOUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord1', 'db_group': 'GroUp2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord2', 'db_group': 'groUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord3', 'db_group': 'GroUp3'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord4', 'db_group': 'GrOUP1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord5', 'db_group': 'GroUp2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 0, 'stringProperty': 'randomWord6', 'db_group': 'group1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 3, 'stringProperty': 'randomWord7', 'db_group': 'group2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 2, 'stringProperty': 'randomWord8', 'db_group': 'GroUp3'}
        ]
        self.computed_properties = [{'name': "cp_lower", 'query': "SELECT VALUE LOWER(c.db_group) FROM c"},
                                   {'name': "cp_power", 'query': "SELECT VALUE POWER(c.val, 2) FROM c"},
                                   {'name': "cp_str_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]

    def computedPropertiesTestCases(self, created_collection):
        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        # Test 0: Negative test, test if using non-existent computed property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_upper = "GROUP2"',
                                           partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 1: Test first computed property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=5)

        # Test 1 Negative: Test if using non-existent string in group property returns nothing
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_lower = "group4"', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 2: Test second computed property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_power = 25',
            partition_key="test",
            expected_count=7)

        # Test 2 Negative: Test Non-Existent POWER
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_power = 16', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 3: Test Third Computed Property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=2)

    def _assert_query_count_eventually(self, container_client, query, partition_key, expected_count):
        # Container replace can take a few seconds before computed-property queries become visible.
        last_count = -1
        for _ in range(8):
            queried_items = list(container_client.query_items(query=query, partition_key=partition_key))
            last_count = len(queried_items)
            if last_count == expected_count:
                return
            time.sleep(1)
        self.assertEqual(last_count, expected_count)

        # Test 3 Negative: Test Str length that isn't there
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_str_len = 3', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

    def test_replace_with_same_computed_properties(self):
        """Replacing a container with the identical computed properties leaves them working.

        The container is created with three computed properties, items are
        written, then it is replaced passing the very same definitions.

        A replace rewrites the whole container definition, so even a no-op
        replace can drop the properties if they are not carried through.
        Afterwards all three must still be queryable, and a name that was never
        defined must still match nothing.

        Query counts are retried rather than checked once, because the service
        applies computed properties in the background after the replace.
        """
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_same_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)
        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties= self.computed_properties)
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        self.computedPropertiesTestCases(replaced_collection)
        self.key_db.delete_container(replaced_collection.id)

    def test_replace_without_computed_properties(self):
        """Replace can add computed properties to a container created without any.

        The container starts with none, items are written, then a replace
        introduces all three for the first time.

        This is the adding path rather than the preserving path: the properties
        have to be sent on a container that has no existing set to merge with,
        and existing items must become queryable through them.
        """
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_without_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        # Replace Container
        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties= self.computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)
        self.computedPropertiesTestCases(replaced_collection)
        self.key_db.delete_container(replaced_collection.id)

    def test_replace_with_new_computed_properties(self):
        """Replace swaps one set of computed properties for a different set.

        The container starts with ``cp_lower``, ``cp_power`` and
        ``cp_str_len``, and is replaced with ``cp_upper`` and ``cp_len``.

        Both halves of the swap are checked: the new names must become
        queryable, and the old ``cp_lower`` must stop matching anything. The
        second half is the one that catches a replace which merges the two sets
        instead of substituting one for the other.
        """
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_new_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        new_computed_properties = [{'name': "cp_upper", 'query': "SELECT VALUE UPPER(c.db_group) FROM c"},
                                   {'name': "cp_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]
        # Replace Container
        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties=new_computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)
        # Check that computed properties were properly sent to replaced container
        self.assertListEqual(new_computed_properties, replaced_collection.read()["computedProperties"])

        # Test 1: Test first computed property
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_upper = "GROUP2"',
            partition_key="test",
            expected_count=3)

        # Test 1 Negative: Test if using non-existent computed property name returns nothing
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=0)

        # Test 2: Test Second Computed Property
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_len = 9',
            partition_key="test",
            expected_count=2)

        # Test 2 Negative: Test Str length using old computed properties name
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=0)
        self.key_db.delete_container(created_collection.id)

    def test_replace_with_incorrect_computed_properties(self):
        """A single dict instead of a list of them is rejected by the service.

        Computed properties must be a list. Passing one bare dict is an easy
        mistake to make, and it has to come back as a 400 saying the input is
        invalid rather than being silently accepted or mangled into something
        the customer did not ask for.
        """
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_incorrect_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        computed_properties = {'name': "cp_lower", 'query': "SELECT VALUE LOWER(c.db_group) FROM c"}

        try:
            # Replace Container with wrong type for computed_properties
            self.key_db.replace_container(
                container=created_collection.id,
                partition_key=PartitionKey(path="/pk"),
                computed_properties= computed_properties
            )
            pytest.fail("Container creation should have failed for invalid input.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "One of the specified inputs is invalid" in e.http_error_message

    def test_replace_with_remove_computed_properties_(self):
        """Replacing without mentioning computed properties removes them entirely.

        The container is created with three, then replaced with no
        ``computed_properties`` argument at all.

        Omitting them means removal, not "leave as they are", and removal has
        to be complete: reading the container afterwards must not contain a
        ``computedProperties`` key, which is why the check is a ``KeyError``
        rather than an empty list.
        """
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_remove_computed_properties_
        created_collection_ref = self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        # Check if computed properties were set
        container = created_collection.read()
        assert self.computed_properties == container["computedProperties"]

        # Replace Container
        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"))
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        # Check if computed properties were not set
        container = replaced_collection.read()

        # If keyError is not raised the test will fail
        with pytest.raises(KeyError):
            computed_properties = container["computedProperties"]
