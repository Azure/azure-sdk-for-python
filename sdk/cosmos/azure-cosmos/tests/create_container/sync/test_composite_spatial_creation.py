# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation assertions copied from main e1c0306c77b2: test_crud_container.py."""

# Preserve policy assertions; retired transport controls are omitted.
# The old headers keyword becomes the supported initial_headers keyword.

import uuid
import pytest
from azure.cosmos import PartitionKey
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosLong
class TestCRUDContainerOperations(SyncCreationCase):

    def test_create_indexing_policy_with_composite_and_spatial_indexes_rust(self):
        db = self.databaseForTest
        indexing_policy = {
            "spatialIndexes": [
                {
                    "path": "/path0/*",
                    "types": ["Point", "LineString", "Polygon", "MultiPolygon"],
                },
                {
                    "path": "/path1/*",
                    "types": ["Point", "LineString", "Polygon", "MultiPolygon"],
                },
            ],
            "compositeIndexes": [
                [
                    {"path": "/path1", "order": "ascending"},
                    {"path": "/path2", "order": "descending"},
                    {"path": "/path3", "order": "ascending"},
                ],
                [
                    {"path": "/path4", "order": "ascending"},
                    {"path": "/path5", "order": "descending"},
                    {"path": "/path6", "order": "ascending"},
                ],
            ],
        }
        created_container = db.create_container(
            id="composite_index_spatial_index" + str(uuid.uuid4()),
            indexing_policy=indexing_policy,
            partition_key=PartitionKey(path="/id", kind="Hash"),
            initial_headers={"Foo": "bar"},
        )
        created_properties = created_container.read()
        read_indexing_policy = created_properties["indexingPolicy"]
        if "localhost" in self.host or "127.0.0.1" in self.host:
            self.assertListEqual(
                indexing_policy["spatialIndexes"],
                read_indexing_policy["spatialIndexes"],
            )
        else:
            self.assertListEqual(
                indexing_policy["spatialIndexes"],
                read_indexing_policy["spatialIndexes"],
            )
        self.assertListEqual(
            indexing_policy["compositeIndexes"],
            read_indexing_policy["compositeIndexes"],
        )
        db.delete_container(container=created_container)
