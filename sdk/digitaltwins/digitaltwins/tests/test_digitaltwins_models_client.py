# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import unittest

# from azure.digitaltwins import DigitalTwinsModelsClient

import pytest

try:
    from unittest.mock import mock
except ImportError:
    # python < 3.3
    from mock import mock

# class TestDigitalTinwsModelsClient(object):
    # def test_constructor(self):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
        
    #     digital_twin_models_client = DigitalTwinsModelsClient(fake_endpoint, fake_credential)
    #     assert isinstance(digital_twin_models_client, DigitalTwinsModelsClient)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinModelsOperations.get_model'
    # )
    # def test_get_model(self, get_by_id):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_model_id = 'digital_twin_id'
    #     digital_twin_models_client = DigitalTwinsModelsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_models(fake_model_id)
    #     get_model.assert_called_with(fake_model_id)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_by_id'
    # )
    # def test_get_digital_twin_with_kwargs(self, get_by_id):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_digital_twin(fake_digital_twin_id, **fake_kwargs)
    #     get_by_id.assert_called_with(fake_digital_twin_id, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add'
    # )
    # def test_upsert_digital_twin(self, add):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_digital_twin = 'digital_twin'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_digital_twin(fake_digital_twin_id, fake_digital_twin)
    #     add.assert_called_with(fake_digital_twin_id, fake_digital_twin)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add'
    # )
    # def test_upsert_digital_twin_with_kwargs(self, add):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_digital_twin = 'digital_twin'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_digital_twin(fake_digital_twin_id, fake_digital_twin, **fake_kwargs)
    #     add.assert_called_with(fake_digital_twin_id, fake_digital_twin, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    # )
    # def test_update_digital_twin(self, update):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_twin_patch = 'twin_patch'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_twin_patch)
    #     update.assert_called_with(fake_digital_twin_id, fake_twin_patch, if_match=None)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    # )
    # def test_update_digital_twin_with_etag(self, update):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_twin_patch = 'twin_patch'
    #     fake_etag = 'etag'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_twin_patch, fake_etag)
    #     update.assert_called_with(fake_digital_twin_id, fake_twin_patch, if_match=fake_etag)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    # )
    # def test_update_digital_twin_with_kwargs(self, update):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_twin_patch = 'twin_patch'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_twin_patch, **fake_kwargs)
    #     update.assert_called_with(fake_digital_twin_id, fake_twin_patch, if_match=None, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update'
    # )
    # def test_update_digital_twin_with_all(self, update):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_twin_patch = 'twin_patch'
    #     fake_etag = 'etag'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_digital_twin(fake_digital_twin_id, fake_twin_patch, fake_etag, **fake_kwargs)
    #     update.assert_called_with(fake_digital_twin_id, fake_twin_patch, if_match=fake_etag, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    # )
    # def test_delete_digital_twin(self, delete):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_digital_twin(fake_digital_twin_id)
    #     delete.assert_called_with(fake_digital_twin_id, if_match=None)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    # )
    # def test_delete_digital_twin_with_etag(self, delete):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_etag = 'etag'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_digital_twin(fake_digital_twin_id, fake_etag)
    #     delete.assert_called_with(fake_digital_twin_id, if_match=fake_etag)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    # )
    # def test_delete_digital_twin_with_kwargs(self, delete):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_digital_twin(fake_digital_twin_id, None, **fake_kwargs)
    #     delete.assert_called_with(fake_digital_twin_id, if_match=None, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete'
    # )
    # def test_delete_digital_twin_with_all(self, delete):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_etag = 'etag'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_digital_twin(fake_digital_twin_id, fake_etag, **fake_kwargs)
    #     delete.assert_called_with(fake_digital_twin_id, if_match=fake_etag, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_component'
    # )
    # def test_get_component(self, get_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_path'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_component(fake_digital_twin_id, fake_component_path)
    #     get_component.assert_called_with(fake_digital_twin_id, fake_component_path)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_component'
    # )
    # def test_get_component_with_kwargs(self, get_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_path'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_component(fake_digital_twin_id, fake_component_path, **fake_kwargs)
    #     get_component.assert_called_with(fake_digital_twin_id, fake_component_path, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    # )
    # def test_update_component(self, update_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_patch'
    #     fake_component_patch = 'component_patch'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_component(fake_digital_twin_id, fake_component_path, fake_component_patch)
    #     update_component.assert_called_with(fake_digital_twin_id, fake_component_path, patch_document=fake_component_patch, if_match=None)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    # )
    # def test_update_component_with_etag(self, update_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_patch'
    #     fake_component_patch = 'component_patch'
    #     fake_etag = 'etag'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_component(fake_digital_twin_id, fake_component_path, fake_component_patch, fake_etag)
    #     update_component.assert_called_with(fake_digital_twin_id, fake_component_path, patch_document=fake_component_patch, if_match=fake_etag)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    # )
    # def test_update_component_with_kwargs(self, update_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_patch'
    #     fake_component_patch = 'component_patch'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_component(fake_digital_twin_id, fake_component_path, fake_component_patch, **fake_kwargs)
    #     update_component.assert_called_with(fake_digital_twin_id, fake_component_path, patch_document=fake_component_patch, if_match=None, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_component'
    # )
    # def test_update_component_with_all(self, update_component):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_patch'
    #     fake_component_patch = 'component_patch'
    #     fake_etag = 'etag'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_component(fake_digital_twin_id, fake_component_path, fake_component_patch, fake_etag, **fake_kwargs)
    #     update_component.assert_called_with(fake_digital_twin_id, fake_component_path, patch_document=fake_component_patch, if_match=fake_etag, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_relationship_by_id'
    # )
    # def test_get_relationship(self, get_relationship_by_id):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_relationship(fake_digital_twin_id, fake_relationship_id)
    #     get_relationship_by_id.assert_called_with(fake_digital_twin_id, fake_relationship_id)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.get_relationship_by_id'
    # )
    # def test_get_relationship_with_kwargs(self, get_relationship_by_id):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.get_relationship(fake_digital_twin_id, fake_relationship_id, **fake_kwargs)
    #     get_relationship_by_id.assert_called_with(fake_digital_twin_id, fake_relationship_id, **fake_kwargs)

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    # )
    # def test_upsert_relationship(self, add_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_relationship(fake_digital_twin_id, fake_relationship_id)
    #     add_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship=None
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    # )
    # def test_upsert_relationship_with_relationship(self, add_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_relationship = 'relationship'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_relationship(fake_digital_twin_id, fake_relationship_id, fake_relationship)
    #     add_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship=fake_relationship
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    # )
    # def test_upsert_relationship_with_kwargs(self, add_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_relationship(fake_digital_twin_id, fake_relationship_id, **fake_kwargs)
    #     add_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship=None,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.add_relationship'
    # )
    # def test_upsert_relationship_with_all(self, add_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_relationship = 'relationship'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.upsert_relationship(fake_digital_twin_id, fake_relationship_id, fake_relationship, **fake_kwargs)
    #     add_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship=fake_relationship,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    # )
    # def test_upsert_relationship(self, update_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_relationship(fake_digital_twin_id, fake_relationship_id)
    #     update_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship_patch=None,
    #         if_match=None,
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    # )
    # def test_upsert_relationship_with_relationship(self, update_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_relationship_patch = 'relationship_patch'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_relationship(fake_digital_twin_id, fake_relationship_id, fake_relationship_patch)
    #     update_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship_patch=fake_relationship_patch,
    #         if_match=None,
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.update_relationship'
    # )
    # def test_upsert_relationship_with_etag(self, update_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_relationship_patch = 'relationship_patch'
    #     fake_etag = 'etag'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.update_relationship(fake_digital_twin_id, fake_relationship_id, fake_relationship_patch, fake_etag)
    #     update_relationship.assert_called_with(
    #         id=fake_digital_twin_id,
    #         relationship_id=fake_relationship_id,
    #         relationship_patch=fake_relationship_patch,
    #         if_match=fake_etag,
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    # )
    # def test_delete_relationship(self, delete_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_relationship(fake_digital_twin_id, fake_relationship_id)
    #     delete_relationship.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_relationship_id,
    #         if_match=None
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    # )
    # def test_delete_relationship_with_etag(self, delete_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_etag = 'etag'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_relationship(fake_digital_twin_id, fake_relationship_id, fake_etag)
    #     delete_relationship.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_relationship_id,
    #         if_match=fake_etag
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.delete_relationship'
    # )
    # def test_delete_relationship_with_kwargs(self, delete_relationship):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_etag = 'etag'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.delete_relationship(fake_digital_twin_id, fake_relationship_id, fake_etag, **fake_kwargs)
    #     delete_relationship.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_relationship_id,
    #         if_match=fake_etag,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    # )
    # def test_list_relationship(self, list_relationships):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.list_relationships(fake_digital_twin_id)
    #     list_relationships.assert_called_with(
    #         fake_digital_twin_id,
    #         relationship_name=None
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    # )
    # def test_list_relationship_with_id(self, list_relationships):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.list_relationships(fake_digital_twin_id, fake_relationship_id)
    #     list_relationships.assert_called_with(
    #         fake_digital_twin_id,
    #         relationship_name=fake_relationship_id
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_relationships'
    # )
    # def test_list_relationship_with_kwargs(self, list_relationships):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_relationship_id = 'relationship_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.list_relationships(fake_digital_twin_id, fake_relationship_id, **fake_kwargs)
    #     list_relationships.assert_called_with(
    #         fake_digital_twin_id,
    #         relationship_name=fake_relationship_id,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_incoming_relationships'
    # )
    # def test_list_incoming_relationship(self, list_incoming_relationships):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.list_incoming_relationships(fake_digital_twin_id)
    #     list_incoming_relationships.assert_called_with(
    #         fake_digital_twin_id
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.list_incoming_relationships'
    # )
    # def test_list_incoming_relationship_with_kwargs(self, list_incoming_relationships):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.list_incoming_relationships(fake_digital_twin_id, **fake_kwargs)
    #     list_incoming_relationships.assert_called_with(
    #         fake_digital_twin_id,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    # )
    # def test_publish_telemetry(self, send_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_payload = 'payload'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_telemetry(fake_digital_twin_id, fake_payload)
    #     send_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         mock.ANY,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    # )
    # def test_publish_telemetry_with_message_id(self, send_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_payload = 'payload'
    #     fake_message_id = 'message_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_telemetry(fake_digital_twin_id, fake_payload, fake_message_id)
    #     send_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_message_id,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_telemetry'
    # )
    # def test_publish_telemetry_with_kwargs(self, send_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_payload = 'payload'
    #     fake_message_id = 'message_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_telemetry(fake_digital_twin_id, fake_payload, fake_message_id, **fake_kwargs)
    #     send_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_message_id,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY,
    #         **fake_kwargs
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    # )
    # def test_publish_component_telemetry(self, send_component_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_path'
    #     fake_payload = 'payload'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_component_telemetry(fake_digital_twin_id, fake_component_path, fake_payload)
    #     send_component_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_component_path,
    #         dt_id=mock.ANY,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    # )
    # def test_publish_component_telemetry_with_message_id(self, send_component_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_path'
    #     fake_payload = 'payload'
    #     fake_message_id = 'message_id'
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_component_telemetry(fake_digital_twin_id, fake_component_path, fake_payload, fake_message_id)
    #     send_component_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_component_path,
    #         dt_id=fake_message_id,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY
    #     )

    # @mock.patch(
    #     'azure.digitaltwins._generated.operations._digital_twins_operations.DigitalTwinsOperations.send_component_telemetry'
    # )
    # def test_publish_component_telemetry_with_kwargs(self, send_component_telemetry):
    #     fake_endpoint = 'endpoint'
    #     fake_credential = 'credential'
    #     fake_digital_twin_id = 'digital_twin_id'
    #     fake_component_path = 'component_path'
    #     fake_payload = 'payload'
    #     fake_message_id = 'message_id'
    #     fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
    #     digital_twin_client = DigitalTwinsClient(fake_endpoint, fake_credential)

    #     digital_twin_client.publish_component_telemetry(fake_digital_twin_id, fake_component_path, fake_payload, fake_message_id, **fake_kwargs)
    #     send_component_telemetry.assert_called_with(
    #         fake_digital_twin_id,
    #         fake_component_path,
    #         dt_id=fake_message_id,
    #         telemetry=fake_payload,
    #         dt_timestamp=mock.ANY,
    #         **fake_kwargs
    #     )
