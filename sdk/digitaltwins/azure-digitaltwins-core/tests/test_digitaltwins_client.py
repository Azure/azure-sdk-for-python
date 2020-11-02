# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import unittest

from azure.digitaltwins.core import DigitalTwinsClient
from azure.core import MatchConditions

import pytest

try:
    from unittest.mock import mock
except ImportError:
    # python < 3.3
    from mock import mock

class TestDigitalTinwsClient(object):
    def test_constructor(self):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'

        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)
        assert isinstance(digital_twin_client, DigitalTwinsClient)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_by_id'
    )
    def test_get_digital_twin(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_digital_twin(fake_digital_twin_id)
        get_by_id.assert_called_with(fake_digital_twin_id)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_by_id'
    )
    def test_get_digital_twin_with_kwargs(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_digital_twin(fake_digital_twin_id, **fake_kwargs)
        get_by_id.assert_called_with(fake_digital_twin_id, **fake_kwargs)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.add'
    )
    def test_upsert_digital_twin(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_digital_twin = 'digital_twin'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_digital_twin(fake_digital_twin_id, fake_digital_twin)
        add.assert_called_with(fake_digital_twin_id, fake_digital_twin)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.add'
    )
    def test_upsert_digital_twin_with_kwargs(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_digital_twin = 'digital_twin'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_digital_twin(fake_digital_twin_id, fake_digital_twin, **fake_kwargs)
        add.assert_called_with(fake_digital_twin_id, fake_digital_twin, **fake_kwargs)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    )
    def test_update_digital_twin(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_json_patch = 'json_patch'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_json_patch)
        update.assert_called_with(fake_digital_twin_id, fake_json_patch, if_match=None)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    )
    def test_update_digital_twin_with_etag(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_json_patch = 'json_patch'
        fake_etag = 'etag'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_json_patch, etag=fake_etag)
        update.assert_called_with(fake_digital_twin_id, fake_json_patch, if_match=None, etag=fake_etag)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    )
    def test_update_digital_twin_with_kwargs(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_json_patch = 'json_patch'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_json_patch, **fake_kwargs)
        update.assert_called_with(fake_digital_twin_id, fake_json_patch, if_match=None, **fake_kwargs)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    )
    def test_update_digital_twin_with_all(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_json_patch = 'json_patch'
        fake_etag = 'etag'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_digital_twin(
            fake_digital_twin_id,
            fake_json_patch,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )
        update.assert_called_with(
            fake_digital_twin_id,
            fake_json_patch,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    )
    def test_delete_digital_twin(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_digital_twin(fake_digital_twin_id)
        delete.assert_called_with(fake_digital_twin_id, if_match=None)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    )
    def test_delete_digital_twin_with_etag(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_etag = 'etag'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_digital_twin(
            fake_digital_twin_id,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )
        delete.assert_called_with(
            fake_digital_twin_id,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    )
    def test_delete_digital_twin_with_kwargs(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_digital_twin(fake_digital_twin_id, **fake_kwargs)
        delete.assert_called_with(fake_digital_twin_id, if_match=None, **fake_kwargs)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    )
    def test_delete_digital_twin_with_all(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_etag = 'etag'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_digital_twin(
            fake_digital_twin_id,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )
        delete.assert_called_with(
            fake_digital_twin_id,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_component'
    )
    def test_get_component(self, get_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'component_path'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_component(fake_digital_twin_id, fake_component_path)
        get_component.assert_called_with(fake_digital_twin_id, fake_component_path)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_component'
    )
    def test_get_component_with_kwargs(self, get_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'component_path'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_component(fake_digital_twin_id, fake_component_path, **fake_kwargs)
        get_component.assert_called_with(fake_digital_twin_id, fake_component_path, **fake_kwargs)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    )
    def test_update_component(self, update_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'json_patch'
        fake_json_patch = 'json_patch'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_component(
            fake_digital_twin_id,
            fake_component_path,
            fake_json_patch
        )
        update_component.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            patch_document=fake_json_patch,
            if_match=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    )
    def test_update_component_with_etag(self, update_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'json_patch'
        fake_json_patch = 'json_patch'
        fake_etag = 'etag'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_component(
            fake_digital_twin_id,
            fake_component_path,
            fake_json_patch,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )
        update_component.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            patch_document=fake_json_patch,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    )
    def test_update_component_with_kwargs(self, update_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'json_patch'
        fake_json_patch = 'json_patch'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_component(
            fake_digital_twin_id,
            fake_component_path,
            fake_json_patch,
            **fake_kwargs
        )
        update_component.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            patch_document=fake_json_patch,
            if_match=None, **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    )
    def test_update_component_with_all(self, update_component):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'json_patch'
        fake_json_patch = 'json_patch'
        fake_etag = 'etag'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_component(
            fake_digital_twin_id,
            fake_component_path,
            fake_json_patch,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )
        update_component.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            patch_document=fake_json_patch,
            if_match='*', etag=fake_etag,
            match_condition=MatchConditions.IfPresent,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_relationship_by_id'
    )
    def test_get_relationship(self, get_relationship_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_relationship(
            fake_digital_twin_id,
            fake_relationship_id
        )
        get_relationship_by_id.assert_called_with(
            fake_digital_twin_id,
            fake_relationship_id
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_relationship_by_id'
    )
    def test_get_relationship_with_kwargs(self, get_relationship_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            **fake_kwargs
        )
        get_relationship_by_id.assert_called_with(
            fake_digital_twin_id,
            fake_relationship_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    )
    def test_upsert_relationship(self, add_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_relationship(
            fake_digital_twin_id,
            fake_relationship_id
        )
        add_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            relationship=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    )
    def test_upsert_relationship_with_relationship(self, add_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_relationship = 'relationship'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            fake_relationship
        )
        add_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            relationship=fake_relationship
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    )
    def test_upsert_relationship_with_kwargs(self, add_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            **fake_kwargs
        )
        add_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            relationship=None,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    )
    def test_upsert_relationship(self, update_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_relationship(
            fake_digital_twin_id,
            fake_relationship_id
        )
        update_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            json_patch=None,
            if_match=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    )
    def test_upsert_relationship_with_relationship(self, update_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_json_patch = 'json_patch'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            fake_json_patch
        )
        update_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            json_patch=fake_json_patch,
            if_match=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    )
    def test_upsert_relationship_with_etag(self, update_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_json_patch = 'json_patch'
        fake_etag = 'etag'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.update_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            fake_json_patch,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )
        update_relationship.assert_called_with(
            id=fake_digital_twin_id,
            relationship_id=fake_relationship_id,
            json_patch=fake_json_patch,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    )
    def test_delete_relationship(self, delete_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_relationship(fake_digital_twin_id, fake_relationship_id)
        delete_relationship.assert_called_with(
            fake_digital_twin_id,
            fake_relationship_id,
            if_match=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    )
    def test_delete_relationship_with_etag(self, delete_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_etag = 'etag'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )
        delete_relationship.assert_called_with(
            fake_digital_twin_id,
            fake_relationship_id,
            if_match='*',
            etag=fake_etag,
            match_condition=MatchConditions.IfPresent
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    )
    def test_delete_relationship_with_kwargs(self, delete_relationship):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_etag = 'etag'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_relationship(
            fake_digital_twin_id,
            fake_relationship_id,
            **fake_kwargs
        )
        delete_relationship.assert_called_with(
            fake_digital_twin_id,
            fake_relationship_id,
            if_match=None,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    )
    def test_list_relationship(self, list_relationships):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_relationships(fake_digital_twin_id)
        list_relationships.assert_called_with(
            fake_digital_twin_id,
            relationship_name=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    )
    def test_list_relationship_with_id(self, list_relationships):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_relationships(
            fake_digital_twin_id,
            fake_relationship_id
        )
        list_relationships.assert_called_with(
            fake_digital_twin_id,
            relationship_name=fake_relationship_id
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    )
    def test_list_relationship_with_kwargs(self, list_relationships):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_relationship_id = 'relationship_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_relationships(
            fake_digital_twin_id,
            fake_relationship_id,
            **fake_kwargs
        )
        list_relationships.assert_called_with(
            fake_digital_twin_id,
            relationship_name=fake_relationship_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_incoming_relationships'
    )
    def test_list_incoming_relationship(self, list_incoming_relationships):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_incoming_relationships(fake_digital_twin_id)
        list_incoming_relationships.assert_called_with(fake_digital_twin_id)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_incoming_relationships'
    )
    def test_list_incoming_relationship_with_kwargs(self, list_incoming_relationships):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_incoming_relationships(
            fake_digital_twin_id,
            **fake_kwargs
        )
        list_incoming_relationships.assert_called_with(
            fake_digital_twin_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    )
    def test_publish_telemetry(self, send_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_payload = 'payload'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_telemetry(
            fake_digital_twin_id,
            fake_payload
        )
        send_telemetry.assert_called_with(
            fake_digital_twin_id,
            mock.ANY,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    )
    def test_publish_telemetry_with_message_id(self, send_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_payload = 'payload'
        fake_message_id = 'message_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_telemetry(
            fake_digital_twin_id,
            fake_payload,
            fake_message_id
        )
        send_telemetry.assert_called_with(
            fake_digital_twin_id,
            fake_message_id,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    )
    def test_publish_telemetry_with_kwargs(self, send_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_payload = 'payload'
        fake_message_id = 'message_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_telemetry(
            fake_digital_twin_id,
            fake_payload,
            fake_message_id,
            **fake_kwargs
        )
        send_telemetry.assert_called_with(
            fake_digital_twin_id,
            fake_message_id,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    )
    def test_publish_component_telemetry(self, send_component_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'component_path'
        fake_payload = 'payload'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_component_telemetry(
            fake_digital_twin_id,
            fake_component_path,
            fake_payload
        )
        send_component_telemetry.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            dt_id=mock.ANY,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    )
    def test_publish_component_telemetry_with_message_id(self, send_component_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'component_path'
        fake_payload = 'payload'
        fake_message_id = 'message_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_component_telemetry(
            fake_digital_twin_id,
            fake_component_path,
            fake_payload,
            fake_message_id
        )
        send_component_telemetry.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            dt_id=fake_message_id,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    )
    def test_publish_component_telemetry_with_kwargs(self, send_component_telemetry):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_digital_twin_id = 'digital_twin_id'
        fake_component_path = 'component_path'
        fake_payload = 'payload'
        fake_message_id = 'message_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.publish_component_telemetry(
            fake_digital_twin_id,
            fake_component_path,
            fake_payload,
            fake_message_id,
            **fake_kwargs
        )
        send_component_telemetry.assert_called_with(
            fake_digital_twin_id,
            fake_component_path,
            dt_id=fake_message_id,
            telemetry=fake_payload,
            dt_timestamp=mock.ANY,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(fake_model_id)
        get_by_id.assert_called_with(fake_model_id, False)

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model_with_model_definition(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(
            fake_model_id,
            include_model_definition=True
        )
        get_by_id.assert_called_with(
            fake_model_id,
            True,
            include_model_definition=True
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model_with_model_kwargs(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(
            fake_model_id,
            include_model_definition=True,
            **fake_kwargs
        )
        get_by_id.assert_called_with(
            fake_model_id,
            True,
            include_model_definition=True,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(
            fake_dependencies_for
        )
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=False,
            digital_twin_models_list_options=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_definition(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(
            fake_dependencies_for,
            include_model_definition=True
        )
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=True,
            digital_twin_models_list_options=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_result_per_page(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(
            fake_dependencies_for,
            results_per_page=42
        )
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=False,
            digital_twin_models_list_options={'max_item_count': 42}
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_kwargs(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        fake_results_per_page = 42
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(
            fake_dependencies_for,
            include_model_definition=True,
            results_per_page=42,
            **fake_kwargs
        )
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=True,
            digital_twin_models_list_options={'max_item_count': 42},
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models()
        add.assert_called_with(
            None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models_with_models(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_models = 'models'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models(fake_models)
        add.assert_called_with(
            fake_models
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models_with_kwargs(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_models = 'models'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models(
            fake_models,
            **fake_kwargs
        )
        add.assert_called_with(
            fake_models,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.update'
    )
    def test_decommission_model(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        json_patch = "{ 'op': 'replace', 'path': '/decommissioned', 'value': true }"
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.decommission_model(fake_model_id)
        update.assert_called_with(
            fake_model_id,
            json_patch
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.update'
    )
    def test_decommission_model_with_kwargs(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        json_patch = "{ 'op': 'replace', 'path': '/decommissioned', 'value': true }"
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.decommission_model(
            fake_model_id,
            **fake_kwargs
        )
        update.assert_called_with(
            fake_model_id,
            json_patch,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.delete'
    )
    def test_delete_model(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.delete_model(fake_model_id)
        delete.assert_called_with(
            fake_model_id
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.delete'
    )
    def test_delete_model_with_kwargs(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.delete_model(
            fake_model_id,
            **fake_kwargs
        )
        delete.assert_called_with(
            fake_model_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.get_by_id'
    )
    def test_get_event_route(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_event_route(fake_event_route_id)
        get_by_id.assert_called_with(
            fake_event_route_id
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.get_by_id'
    )
    def test_get_event_rout_with_kwargs(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.get_event_route(
            fake_event_route_id,
            **fake_kwargs
        )
        get_by_id.assert_called_with(
            fake_event_route_id,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_event_routes()
        list.assert_called_with(
            event_routes_list_options=None
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes_with_result_per_page(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_results_per_page = 42
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_event_routes(
            results_per_page=fake_results_per_page
        )
        list.assert_called_with(
            event_routes_list_options={'max_item_count': fake_results_per_page}
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.list'
    )
    def test_list_event_routes_with_kwargs(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_results_per_page = 42
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.list_event_routes(**fake_kwargs)
        list.assert_called_with(
            event_routes_list_options=None,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.add'
    )
    def test_upsert_event_route(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_event_route = 'event_route'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_event_route(
            fake_event_route_id,
            fake_event_route
        )
        add.assert_called_with(
            fake_event_route_id,
            fake_event_route
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.add'
    )
    def test_upsert_event_route_with_kwargs(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_event_route = 'event_route'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.upsert_event_route(
            fake_event_route_id,
            fake_event_route,
            **fake_kwargs
        )
        add.assert_called_with(
            fake_event_route_id,
            fake_event_route,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.delete'
    )
    def test_delete_event_route(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_event_route(fake_event_route_id)
        delete.assert_called_with(
            fake_event_route_id
        )

    @mock.patch(
        'azure.digitaltwins.core._generated.operations._event_routes_operations.EventRoutesOperations.delete'
    )
    def test_delete_event_route_with_kwargs(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_event_route_id = 'event_route_id'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

        digital_twin_client.delete_event_route(
            fake_event_route_id,
            **fake_kwargs
        )
        delete.assert_called_with(
            fake_event_route_id,
            **fake_kwargs
        )
