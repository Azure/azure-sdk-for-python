# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from os import pathsep
import pytest
import uuid

from devtools_testutils import AzureTestCase
from _preparer import DigitalTwinsRGPreparer, DigitalTwinsPreparer

from azure.digitaltwins.core.aio import DigitalTwinsClient
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceNotFoundError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotModifiedError
)

BUILDING_MODEL_ID = "dtmi:samples:DTTestBuilding;1"


class DigitalTwinsTestsAsync(AzureTestCase):

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

    async def _set_up_models(self, client, dt_id):
        await self._clean_up_models(client)
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
        await client.create_models([dtdl_model_building])

        try:
            await client.delete_digital_twin(dt_id)
        except ResourceNotFoundError:
            pass

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_simple_digitaltwin_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin["AverageTemperature"] == dtdl_digital_twins_building_twin["AverageTemperature"]
        assert created_twin.get('$etag')
        assert created_twin.get('$dtId') == digital_twin_id

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_digitaltwin_without_model_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": "dtmi:samples:Building;2"
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(HttpResponseError):
            await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_invalid_digitaltwin_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "LowestTemperature": 68,
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        with pytest.raises(HttpResponseError):
            await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_digitaltwin_conditionally_if_missing_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(
            digital_twin_id,
            dtdl_digital_twins_building_twin,
            match_condition=MatchConditions.IfMissing)
        assert created_twin.get('$dtId') == digital_twin_id

        with pytest.raises(ResourceExistsError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfMissing)

    @pytest.mark.skip("Conditional etag does not appear to be supported")
    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_create_digitaltwin_conditionally_if_modified_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == digital_twin_id

        with pytest.raises(ResourceNotModifiedError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfModified,
                etag=created_twin.get('$etag'))

        dtdl_digital_twins_building_twin["AverageTemperature"] = 69
        updated_twin = await client.upsert_digital_twin(
            digital_twin_id,
            dtdl_digital_twins_building_twin,
            match_condition=MatchConditions.IfModified,
            etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        assert created_twin.get('$dtId') == updated_twin.get('$dtId')
        assert created_twin["AverageTemperature"] != updated_twin["AverageTemperature"]

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_upsert_simple_digitaltwin_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == digital_twin_id

        dtdl_digital_twins_building_twin["AverageTemperature"] = 69
        upserted_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin.get('$dtId') == upserted_twin.get('$dtId')
        assert created_twin["AverageTemperature"] != upserted_twin["AverageTemperature"]

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_upsert_digitaltwin_invalid_conditions_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ValueError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfMissing,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfModified)
        
        with pytest.raises(ValueError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfNotModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.upsert_digital_twin(
                digital_twin_id,
                dtdl_digital_twins_building_twin,
                match_condition=MatchConditions.IfPresent)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_get_digitaltwin_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        twin = await client.get_digital_twin(digital_twin_id)
        assert twin == created_twin

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_get_digitaltwin_not_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.get_digital_twin(self.create_random_name('digitalTwin-'))

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_digitaltwin_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        deleted = await client.delete_digital_twin(digital_twin_id)
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            await client.get_digital_twin(digital_twin_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_digitaltwin_not_existing_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.delete_digital_twin(self.create_random_name('digitalTwin-'))

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_digitaltwin_conditionally_if_not_modified_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        with pytest.raises(ResourceModifiedError):
            await client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')

        deleted = await client.delete_digital_twin(
            digital_twin_id,
            match_condition=MatchConditions.IfNotModified,
            etag=created_twin['$etag'])
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            await client.get_digital_twin(digital_twin_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_digitaltwin_conditionally_if_present_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        deleted = await client.delete_digital_twin(
            digital_twin_id,
            match_condition=MatchConditions.IfPresent)
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            await client.get_digital_twin(digital_twin_id)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_delete_digitaltwin_invalid_conditions_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ValueError):
            await client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfNotModified)
        
        with pytest.raises(ValueError):
            await client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.delete_digital_twin(
                digital_twin_id,
                match_condition=MatchConditions.IfMissing)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_replace_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        assert created_twin['AverageTemperature'] == 68
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]

        update = await client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = await client.get_digital_twin(digital_twin_id)
        assert updated_twin['AverageTemperature'] == 42

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_remove_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "remove",
                "path": "/AverageTemperature",
            }
        ]

        update = await client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = await client.get_digital_twin(digital_twin_id)
        assert 'AverageTemperature' not in updated_twin

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_add_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "add",
                "path": "/TemperatureUnit",
                "value": "Celsius"
            }
        ]

        update = await client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = await client.get_digital_twin(digital_twin_id)
        assert updated_twin['TemperatureUnit'] == "Celsius"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_multiple_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

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

        update = await client.update_digital_twin(digital_twin_id, patch)
        assert update is None
        updated_twin = await client.get_digital_twin(digital_twin_id)
        assert updated_twin['TemperatureUnit'] == "Celsius"
        assert updated_twin['AverageTemperature'] == 42

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_invalid_patch_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        patch = [
            {
                "op": "move",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(HttpResponseError):
            await client.update_digital_twin(digital_twin_id, patch)
        
        patch = {
            "AverageTemperature": 42
        }
        with pytest.raises(HttpResponseError):
            await client.update_digital_twin(digital_twin_id, patch)

        patch = [{}]
        with pytest.raises(HttpResponseError):
            await client.upsert_digital_twin(digital_twin_id, patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_conditionally_if_not_match_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        created_twin = await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(ResourceModifiedError):
            await client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        await client.update_digital_twin(
            digital_twin_id,
            patch,
            match_condition=MatchConditions.IfNotModified,
            etag=created_twin['$etag'])
        updated = await client.get_digital_twin(digital_twin_id)
        assert updated['AverageTemperature'] == 42

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_conditionally_if_present_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await self._set_up_models(client, digital_twin_id)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        await client.update_digital_twin(
            digital_twin_id,
            patch,
            match_condition=MatchConditions.IfPresent)
        updated = await client.get_digital_twin(digital_twin_id)
        assert updated['AverageTemperature'] == 42

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_invalid_conditions_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        client = self._get_client(digitaltwin.host_name)
        patch = [
            {
                "op": "replace",
                "path": "/AverageTemperature",
                "value": 42
            }
        ]
        with pytest.raises(ValueError):
            await client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfNotModified)
        
        with pytest.raises(ValueError):
            await client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            await client.update_digital_twin(
                digital_twin_id,
                patch,
                match_condition=MatchConditions.IfMissing)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_update_digitaltwin_not_existing_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        patch = [
            {
                "op": "replace",
                "path": "/Property1",
                "value": 42
            }
        ]
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.update_digital_twin(digital_twin_id, patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_query_digitaltwins_async(self, resource_group, location, digitaltwin):
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68,
            "TemperatureUnit": "Celsius"
        }
        client = self._get_client(digitaltwin.host_name)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        dt_ids = []
        async for t in client.query_twins('SELECT * FROM digitaltwins'):
            dt_ids.append(t["$dtId"])
        assert digital_twin_id in dt_ids

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_query_digitaltwins_invalid_expression_async(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(HttpResponseError):
            async for t in client.query_twins("foo"):
                print(t)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_publish_telemetry(self, resource_group, location, digitaltwin):
        # TODO: How to validate this test? It seems to pass regardless
        telemetry = {"ComponentTelemetry1": 5}
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68
        }
        client = self._get_client(digitaltwin.host_name)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        published = await client.publish_telemetry(digital_twin_id, telemetry)
        assert published is None

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_publish_telemetry_with_message_id(self, resource_group, location, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5}
        digital_twin_id = self.create_random_name('digitalTwin-')
        dtdl_digital_twins_building_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68
        }
        client = self._get_client(digitaltwin.host_name)
        await client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)

        published = await client.publish_telemetry(digital_twin_id, telemetry, message_id=self.create_random_name('message-'))
        assert published is None

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    async def test_publish_telemetry_not_existing(self, resource_group, location, digitaltwin):
        telemetry = {"ComponentTelemetry1": 5}
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            await client.publish_telemetry("foo", telemetry)
