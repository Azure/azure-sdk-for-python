# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import time

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceNotFoundError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotModifiedError
)
from azure.digitaltwins.core import DigitalTwinsClient
from devtools_testutils import AzureRecordedTestCase


BUILDING_MODEL_ID = "dtmi:samples:DTTestBuilding;1"


class TestDigitalTwins(AzureRecordedTestCase):

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

    def _set_up_models(self, client, dt_id):
        self._clean_up_models(client)
        dtdl_model_building = {
            "@id": BUILDING_MODEL_ID,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Building",
            "contents": [
                {
                "@type": "Property",
                "name": "AverageTemperature",
                "schema": "double"
                },
                {
                "@type": "Property",
                "name": "TemperatureUnit",
                "schema": "string"
                }
            ]
        }
        client.create_models([dtdl_model_building])
        try:
            client.delete_digital_twin(dt_id)
        except ResourceNotFoundError:
            pass

    def test_create_simple_digitaltwin(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin["AverageTemperature"] == dtdl_digital_twins_building_twin["AverageTemperature"]
        assert created_twin.get('$etag')
        assert created_twin.get('$dtId') == digital_twin_id

    def test_create_digitaltwin_without_model(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": "dtmi:samples:Building;2"
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(HttpResponseError):
            client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

    def test_create_invalid_digitaltwin(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "LowestTemperature": 68,
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        with pytest.raises(HttpResponseError):
            client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

    def test_create_digitaltwin_conditionally_if_missing(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(
            digital_twin_id,
            dtdl_digital_twins_building_twin,
            match_condition=MatchConditions.IfMissing)
        assert created_twin.get('$dtId') == digital_twin_id

        with pytest.raises(ResourceExistsError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfMissing)

    @pytest.mark.skip("Conditional etag does not appear to be supported")
    def test_create_digitaltwin_conditionally_if_modified(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == digital_twin_id

        with pytest.raises(ResourceNotModifiedError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfModified,
                etag=created_twin.get('$etag'))

        dtdl_digital_twins_building_twin["AverageTemperature"] = 69
        updated_twin = client.upsert_digital_twin(
            digital_twin_id,
            dtdl_digital_twins_building_twin,
            match_condition=MatchConditions.IfModified,
            etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        assert created_twin.get('$dtId') == updated_twin.get('$dtId')
        assert created_twin["AverageTemperature"] != updated_twin["AverageTemperature"]

    def test_upsert_simple_digitaltwin(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == digital_twin_id

        dtdl_digital_twins_building_twin["AverageTemperature"] = 69
        upserted_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == upserted_twin.get('$dtId')
        assert created_twin["AverageTemperature"] != upserted_twin["AverageTemperature"]

    def test_upsert_digitaltwin_invalid_conditions(self, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ValueError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfMissing,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfModified)

        with pytest.raises(ValueError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfNotModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfPresent)

    def test_get_digitaltwin(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        twin = client.get_digital_twin(digital_twin_id)
        assert twin == created_twin

    def test_get_digitaltwin_not_existing(self, recorded_test, digitaltwin):
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ResourceNotFoundError):
            client.get_digital_twin(self.create_random_name('digitalTwin-'))

    def test_delete_digitaltwin(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        deleted = client.delete_digital_twin(digital_twin_id)
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_digital_twin(digital_twin_id)

    def test_delete_digitaltwin_not_existing(self, recorded_test, digitaltwin):
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ResourceNotFoundError):
            client.delete_digital_twin(self.create_random_name('digitalTwin-'))

    def test_delete_digitaltwin_conditionally_if_not_modified(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        with pytest.raises(ResourceModifiedError):
            client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')

        deleted = client.delete_digital_twin(
            digital_twin_id,
            match_condition=MatchConditions.IfNotModified,
            etag=created_twin['$etag'])
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_digital_twin(digital_twin_id)

    def test_delete_digitaltwin_conditionally_if_present(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        deleted = client.delete_digital_twin(
            digital_twin_id,
            match_condition=MatchConditions.IfPresent)
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_digital_twin(digital_twin_id)

    def test_delete_digitaltwin_invalid_conditions(self, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ValueError):
            client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfNotModified)

        with pytest.raises(ValueError):
            client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfMissing)

    def test_update_digitaltwin_replace(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin['AverageTemperature'] == 68
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]

        update = client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = client.get_digital_twin(digital_twin_id)
        assert updated_twin['AverageTemperature'] == 42

    def test_update_digitaltwin_remove(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "remove",
                "path": "/AverageTemperature",
            }
        ]

        update = client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = client.get_digital_twin(digital_twin_id)
        assert 'AverageTemperature' not in updated_twin

    def test_update_digitaltwin_add(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "add",
                "path": "/TemperatureUnit",
                "value": "Celsius"
            }
        ]

        update = client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = client.get_digital_twin(digital_twin_id)
        assert updated_twin['TemperatureUnit'] == "Celsius"

    def test_update_digitaltwin_multiple(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "add",
                "path": "/TemperatureUnit",
                "value": "Celsius"
            },
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]

        update = client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = client.get_digital_twin(digital_twin_id)
        assert updated_twin['TemperatureUnit'] == "Celsius"
        assert updated_twin['AverageTemperature'] == 42

    def test_update_digitaltwin_invalid_patch(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "move",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_digital_twin(digital_twin_id, patch)

        patch = {
            "AverageTemperature": 42
        }
        with pytest.raises(HttpResponseError):
            client.update_digital_twin(digital_twin_id, patch)

        patch = [{}]
        with pytest.raises(HttpResponseError):
            client.upsert_digital_twin(digital_twin_id, patch)

    def test_update_digitaltwin_conditionally_if_not_match(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(ResourceModifiedError):
            client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        client.update_digital_twin(
            digital_twin_id,
            patch,
            match_condition=MatchConditions.IfNotModified,
            etag=created_twin['$etag'])
        updated = client.get_digital_twin(digital_twin_id)
        assert updated['AverageTemperature'] == 42

    def test_update_digitaltwin_conditionally_if_present(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        self._set_up_models(client, digital_twin_id)
        created_twin = client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        client.update_digital_twin(
            digital_twin_id,
            patch,
            match_condition=MatchConditions.IfPresent)
        updated = client.get_digital_twin(digital_twin_id)
        assert updated['AverageTemperature'] == 42

    def test_update_digitaltwin_invalid_conditions(self, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        client = self._get_client(digitaltwin["endpoint"])
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(ValueError):
            client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfNotModified)

        with pytest.raises(ValueError):
            client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfMissing)

    def test_update_digitaltwin_not_existing(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        patch = [
            {
                "op": "replace",
                "path": "/Property1",
                "value": 42
            }
        ]
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ResourceNotFoundError):
            client.update_digital_twin(digital_twin_id, patch)

    def test_query_digitaltwins(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        digital_twin_id = "adt-pp3"
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        if self.is_live:
            # Wait for digital twin to reflect on service side.
            time.sleep(10)
        dt_ids = [t["$dtId"] for t in client.query_twins('SELECT * FROM digitaltwins')]
        assert digital_twin_id in dt_ids

    def test_query_digitaltwins_invalid_expression(self, recorded_test, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(HttpResponseError):
            list(client.query_twins("foo"))

    def test_publish_telemetry(self, recorded_test, digitaltwin):
        # TODO: How to validate this test? It seems to pass regardless
        telemetry = {"ComponentTelemetry1": 5}
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68
        }
        client = self._get_client(digitaltwin["endpoint"])
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        published = client.publish_telemetry(digital_twin_id, telemetry)
        assert published is None

    def test_publish_telemetry_with_message_id(self, recorded_test, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5}
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68
        }
        client = self._get_client(digitaltwin["endpoint"])
        client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        published = client.publish_telemetry(digital_twin_id, telemetry, message_id=self.create_random_name('message-'))
        assert published is None

    def test_publish_telemetry_not_existing(self, recorded_test, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5}
        client = self._get_client(digitaltwin["endpoint"])
        with pytest.raises(ResourceNotFoundError):
            client.publish_telemetry("foo", telemetry)
