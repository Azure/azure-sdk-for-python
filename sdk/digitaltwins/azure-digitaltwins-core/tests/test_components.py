# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import uuid

from devtools_testutils import AzureTestCase
from _preparer import DigitalTwinsRGPreparer, DigitalTwinsPreparer

from azure.digitaltwins.core import DigitalTwinsClient, DigitalTwinsModelData
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceNotFoundError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError
)

MODEL_ID = "dtmi:com:samples:DTComponentTestsModel;1"
COMPONENT_ID = "dtmi:com:samples:DTComponentTestsComponent;1"
DIGITAL_TWIN_ID = "DTComponentTestsTempTwin"


class DigitalTwinsComponentTests(AzureTestCase):

    def _get_client(self, endpoint, **kwargs):
        credential = self.get_credential(DigitalTwinsClient)
        return self.create_client_from_credential(
            DigitalTwinsClient,
            credential,
            endpoint=endpoint,
            **kwargs)

    def _clean_up_models(self, client, *models):
        models = [m.id for m in client.list_models()]
        while models:
            print("Cleaning up {} models".format(len(models)))
            for model in models:
                try:
                    client.delete_model(model)
                except:
                    pass
            models = [m.id for m in client.list_models()]

    def _set_up_models(self, client):
        self._clean_up_models(client)
        component = {
            "@id": COMPONENT_ID,
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
            "@id": MODEL_ID,
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
                "schema": COMPONENT_ID
            },
            {
                "@type": "Telemetry",
                "name": "Telemetry1",
                "schema": "integer"
            }
            ]
        }
        client.create_models([component, model])

        temporary_twin = {
            "$metadata": {
                "$model": MODEL_ID
            },
            "Prop1": "value",
            "Component1": {
                "$metadata": {},
                "ComponentProp1": "value1"
            }
        }
        client.upsert_digital_twin(DIGITAL_TWIN_ID, temporary_twin)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_get_component_not_existing(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.get_component(DIGITAL_TWIN_ID, "Component3")
        
        with pytest.raises(ResourceNotFoundError):
            client.get_component("foo", "Component1")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_get_component_simple(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" in component
        assert component["ComponentProp1"] == "value1"
        assert "ComponentTelemetry1" not in component

        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        assert twin["Component1"]["ComponentProp1"] == "value1"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_replace(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            }
        ]
        update = client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        assert update is None
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" in component
        assert component["ComponentProp1"] == "value2"

        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        assert twin["Component1"]["ComponentProp1"] == "value2"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_remove(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        patch = [
            {
                "op": "remove",
                "path": "/ComponentProp1",
            }
        ]

        update = client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        assert update is None
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" not in component

        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        assert "ComponentProp1" not in twin["Component1"]

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_add(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        patch = [
            {
                "op": "add",
                "path": "/ComponentProp1",
                "value": "5"
            }
        ]

        update = client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        assert update is None
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" in component
        assert component["ComponentProp1"] == "5"

        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        assert twin["Component1"]["ComponentProp1"] == "5"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_multiple(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            },
            {
                "op": "remove",
                "path": "/ComponentProp1",
            }
        ]

        update = client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        assert update is None
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" not in component

        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        assert "ComponentProp1" not in twin["Component1"]

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_invalid_patch(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        patch = [
            {
                "op": "move",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        
        patch = {
            "AverageTemperature": 42
        }
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component1", patch)

        patch = [{}]
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
    
        patch = [
            {
                "op": "add",
                "path": "/ComponentProp2",
                "value": "5"
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component1", patch)
        
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": 42
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component1", patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_conditionally_if_not_modified(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        twin = client.get_digital_twin(DIGITAL_TWIN_ID)
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            }
        ]
        with pytest.raises(ResourceModifiedError):
            client.update_component(
                DIGITAL_TWIN_ID,
                "Component1",
                patch,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        client.update_component(
            DIGITAL_TWIN_ID,
            "Component1",
            patch,
            match_condition=MatchConditions.IfNotModified,
            etag=twin['$etag'])
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" in component
        assert component["ComponentProp1"] == "value2"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_conditionally_if_present(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            }
        ]
        client.update_component(
            DIGITAL_TWIN_ID,
            "Component1",
            patch,
            match_condition=MatchConditions.IfPresent)
        component = client.get_component(DIGITAL_TWIN_ID, "Component1")
        assert "ComponentProp1" in component
        assert component["ComponentProp1"] == "value2"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_invalid_conditions(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            }
        ]
        with pytest.raises(ValueError):
            client.update_component(
                DIGITAL_TWIN_ID,
                "Component1",
                patch,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_component(
                DIGITAL_TWIN_ID,
                "Component1",
                patch,
                match_condition=MatchConditions.IfNotModified)
        
        with pytest.raises(ValueError):
            client.update_component(
                DIGITAL_TWIN_ID,
                "Component1",
                patch,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_component(
                DIGITAL_TWIN_ID,
                "Component1",
                patch,
                match_condition=MatchConditions.IfMissing)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_component_not_existing(self, resource_group, location, digitaltwin):
        patch = [
            {
                "op": "replace",
                "path": "/ComponentProp1",
                "value": "value2"
            }
        ]
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(HttpResponseError):
            client.update_component(DIGITAL_TWIN_ID, "Component2", patch)
        
        with pytest.raises(ResourceNotFoundError):
            client.update_component("foo", "Component2", patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_publish_component_telemetry(self, resource_group, location, digitaltwin):
        # TODO: How to validate this test? It seems to pass regardless
        telemetry = {"ComponentTelemetry1": 5} # ComponentTelemetry1
        client = self._get_client(digitaltwin.host_name)
        client.publish_component_telemetry(
            DIGITAL_TWIN_ID,
            "Component1",
            telemetry
        )

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_publish_component_telemetry_with_message_id(self, resource_group, location, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5} # ComponentTelemetry1
        client = self._get_client(digitaltwin.host_name)
        client.publish_component_telemetry(
            DIGITAL_TWIN_ID,
            "Component1",
            telemetry,
            message_id=self.create_random_name('message-')
        )

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_publish_component_telemetry_not_existing(self, resource_group, location, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5}
        client = self._get_client(digitaltwin.host_name)

        with pytest.raises(ResourceNotFoundError):
            client.publish_component_telemetry(
                "foo",
                "Component1",
                telemetry
            )
        with pytest.raises(HttpResponseError):
            client.publish_component_telemetry(
                "foo",
                "Component2",
                telemetry
            )