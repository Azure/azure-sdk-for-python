# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import unittest

from azure.digitaltwins import DigitalTwinModelsClient

import pytest

try:
    from unittest.mock import mock
except ImportError:
    # python < 3.3
    from mock import mock

class TestDigitalTinwsModelsClient(object):
    def test_constructor(self):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)
        assert isinstance(digital_twin_models_client, DigitalTwinModelsClient)

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(fake_model_id)
        get_by_id.assert_called_with(
            fake_model_id,
            False
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model_with_model_definition(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_definition = True
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(fake_model_id, fake_model_definition)
        get_by_id.assert_called_with(
            fake_model_id,
            fake_model_definition
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.get_by_id'
    )
    def test_get_model_with_model_kwargs(self, get_by_id):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_definition = True
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.get_model(fake_model_id, fake_model_definition, **fake_kwargs)
        get_by_id.assert_called_with(
            fake_model_id,
            fake_model_definition,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(fake_dependencies_for)
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=False,
            digital_twin_models_list_options={'max_item_count': -1}
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_definition(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        fake_model_definition = True
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(fake_dependencies_for, fake_model_definition)
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=fake_model_definition,
            digital_twin_models_list_options={'max_item_count': -1}
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_max_item_count(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        fake_model_definition = True
        fake_max_item_count = 42
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(fake_dependencies_for, fake_model_definition, fake_max_item_count)
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=fake_model_definition,
            digital_twin_models_list_options={'max_item_count': 42}
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.list'
    )
    def test_list_models_with_model_kwargs(self, list):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_dependencies_for = 'dependencies_for'
        fake_model_definition = True
        fake_max_item_count = 42
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.list_models(fake_dependencies_for, fake_model_definition, fake_max_item_count, **fake_kwargs)
        list.assert_called_with(
            dependencies_for=fake_dependencies_for,
            include_model_definition=fake_model_definition,
            digital_twin_models_list_options={'max_item_count': 42},
            **fake_kwargs
        )
 
    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models()
        add.assert_called_with(
            None
        )
 
    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models_with_models(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_models = 'models'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models(fake_models)
        add.assert_called_with(
            fake_models
        )
 
    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.add'
    )
    def test_create_models_with_kwargs(self, add):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_models = 'models'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.create_models(fake_models, **fake_kwargs)
        add.assert_called_with(
            fake_models,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.update'
    )
    def test_decommission_model(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.decommission_model(fake_model_id, fake_model_patch)
        update.assert_called_with(
            fake_model_id,
            fake_model_patch
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.update'
    )
    def test_decommission_model_with_kwargs(self, update):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.decommission_model(fake_model_id, fake_model_patch, **fake_kwargs)
        update.assert_called_with(
            fake_model_id,
            fake_model_patch,
            **fake_kwargs
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.delete'
    )
    def test_delete_model(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.delete_model(fake_model_id)
        delete.assert_called_with(
            fake_model_id
        )

    @mock.patch(
        'azure.digitaltwins._generated.operations._digital_twin_models_operations.DigitalTwinModelsOperations.delete'
    )
    def test_delete_model_with_kwargs(self, delete):
        fake_endpoint = 'endpoint'
        fake_credential = 'credential'
        fake_model_id = 'model_id'
        fake_model_patch = 'model_patch'
        fake_kwargs = {'par1_key':'par1_val', 'par2_key':2}
        digital_twin_models_client = DigitalTwinModelsClient(fake_endpoint, fake_credential)

        digital_twin_models_client.delete_model(fake_model_id, **fake_kwargs)
        delete.assert_called_with(
            fake_model_id,
            **fake_kwargs
        )
