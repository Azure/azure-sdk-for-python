# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import random
import asyncio

from devtools_testutils import AzureTestCase
from _preparer import DigitalTwinsRGPreparer, DigitalTwinsPreparer

from azure.digitaltwins.core.aio import DigitalTwinsClient
from azure.digitaltwins.core import DigitalTwinsModelData
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, ResourceExistsError


class DigitalTwinsModelsTestsAsync(AzureTestCase):

    def _get_client(self, endpoint, **kwargs):
        credential = self.get_credential(DigitalTwinsClient, is_async=True)
        return self.create_client_from_credential(
            DigitalTwinsClient,
            credential,
            endpoint=endpoint,
            **kwargs)

    async def _clean_up_models(self, client, *models):
        models = []
        async for m in client.list_models():
            models.append(m)
        while models:
            print("Cleaning up {} models".format(len(models)))
            for model in models:
                try:
                    await client.delete_model(model.id)
                except:
                    pass
            models = []
            async for m in client.list_models():
                models.append(m)
    
    async def _get_unique_component_id(self, client):
        id = "dtmi:com:samples:{};1".format(self.create_random_name("ComponentModel"))
        try:
            await client.get_model(id)
        except ResourceNotFoundError:
            return id
        await self._clean_up_models(client)
        return id
    
    async def _get_unique_model_id(self, client):
        id =  "dtmi:com:samples:{};1".format(self.create_random_name("TempModel"))
        try:
            await client.get_model(id)
        except ResourceNotFoundError:
            return id
        await self._clean_up_models(client)
        return id

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_models_empty_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(HttpResponseError):
            await client.create_models([])

        with pytest.raises(HttpResponseError):
            await client.create_models([{}])
        
        with pytest.raises(HttpResponseError):
            await client.create_models(None)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_models_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        model_id = await self._get_unique_model_id(client)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }

        model = {
            "@id": model_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "TempModel",
            "contents": [
            {
                "@type": "Property",
                "name": "Prop1",
                "schema": "string"
            },
            {
                "@type": "Component",
                "name": "Component1",
                "schema": component_id
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        models = await client.create_models([component, model])
        assert isinstance(models, list)
        assert len(models) == 2
        assert isinstance(models[0], DigitalTwinsModelData)
        assert models[0].id == component_id
        assert isinstance(models[1], DigitalTwinsModelData)
        assert models[1].id == model_id

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_model_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        model_id = await self._get_unique_model_id(client)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }

        model = {
            "@id": model_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "TempModel",
            "contents": [
            {
                "@type": "Property",
                "name": "Prop1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        models = await client.create_models([model])
        assert len(models) == 1
        with pytest.raises(ResourceExistsError):
            await client.create_models([component, model])
        with pytest.raises(ResourceNotFoundError):
            await client.get_model(component_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_model_invalid_model_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        model = {
            "@context": "dtmi:dtdl:context;2",
            "displayName": "TempModel",
            "contents": [
            {
                "@type": "Property",
                "name": "Prop1",
                "schema": "string"
            },
            {
                "@type": "Component",
                "name": "Component1",
                "schema": component_id
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        with pytest.raises(HttpResponseError):
            await client.create_models([model])

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_model_invalid_reference_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        model_id = await self._get_unique_model_id(client)
        model = {
            "@id": model_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "TempModel",
            "contents": [
            {
                "@type": "Property",
                "name": "Prop1",
                "schema": "string"
            },
            {
                "@type": "Component",
                "name": "Component1",
                "schema": component_id
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        with pytest.raises(HttpResponseError):
            await client.create_models([model])

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_get_model_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        models = await client.create_models([component])
        model = await client.get_model(component_id)
        assert models[0].id == model.id
        assert model.id == component_id
        assert model.model is None

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_get_model_with_definition_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": ["dtmi:dtdl:context;2"],
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        models = await client.create_models([component])
        model = await client.get_model(component_id, include_model_definition=True)

        assert models[0].id == model.id
        assert model.id == component_id
        assert model.model == component

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_get_model_not_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.get_model("dtmi:com:samples:NonExistingModel;1")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_list_models_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": ["dtmi:dtdl:context;2"],
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])
        listed_models = []
        async for m in client.list_models(include_model_definition=True):
            listed_models.append(m.id)
        assert len(listed_models) >= 1
        assert component_id in listed_models

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_list_models_with_definition_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": ["dtmi:dtdl:context;2"],
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])
        listed_models = []
        async for m in client.list_models(include_model_definition=True):
            listed_models.append(m.model)
        assert len(listed_models) >= 1
        assert component in listed_models
        assert all(listed_models)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_decommission_model_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])
        model = await client.get_model(component_id)
        assert not model.decommissioned

        decommissioned = await client.decommission_model(component_id)
        assert decommissioned is None

        model = await client.get_model(component_id)
        assert model.decommissioned

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_decommission_model_not_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.decommission_model("dtmi:com:samples:NonExistingModel;1")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_decommission_model_already_decommissioned_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])
        model = await client.get_model(component_id)
        assert not model.decommissioned

        await client.decommission_model(component_id)
        await client.decommission_model(component_id)

        model = await client.get_model(component_id)
        assert model.decommissioned

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_model_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])

        deleted = await client.delete_model(component_id)
        assert deleted is None

        with pytest.raises(ResourceNotFoundError):
            await client.get_model(component_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_model_not_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.delete_model("dtmi:com:samples:NonExistingModel;1")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_model_already_deleted_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component])
        await client.delete_model(component_id)
        with pytest.raises(ResourceNotFoundError):
            await client.delete_model(component_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_models_with_dependencies_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        component_id = await self._get_unique_component_id(client)
        model_id = await self._get_unique_model_id(client)
        component = {
            "@id": component_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Component1",
            "contents": [
            {
                "@type": "Property",
                "name": "ComponentProp1",
                "schema": "string"
            },
            {
                "@type": "Telemetry",
                "name": "ComponentTelemetry1",
                "schema": "integer"
            }
            ]
        }

        model = {
            "@id": model_id,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "TempModel",
            "contents": [
            {
                "@type": "Property",
                "name": "Prop1",
                "schema": "string"
            },
            {
                "@type": "Component",
                "name": "Component1",
                "schema": component_id
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        await client.create_models([component, model])
        with pytest.raises(ResourceExistsError):
            await client.delete_model(component_id)
        
        await client.get_model(component_id)
        await client.delete_model(model_id)
        await client.delete_model(component_id)
        with pytest.raises(ResourceNotFoundError):
            await client.get_model(component_id)
