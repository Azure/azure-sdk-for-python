# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import uuid

from devtools_testutils import AzureTestCase
from _preparer import DigitalTwinsRGPreparer, DigitalTwinsPreparer

from azure.digitaltwins.core import DigitalTwinsClient
from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceNotFoundError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotModifiedError
)

BUILDING_MODEL_ID = "dtmi:samples:Building;1"
FLOOR_MODEL_ID = "dtmi:samples:Floor;1"
ROOM_MODEL_ID = "dtmi:samples:Room;1"
BUILDING_DIGITAL_TWIN = "DTRelationshipTestsBuildingTwin"
FLOOR_DIGITAL_TWIN = "DTRelationshipTestsFloorTwin"
ROOM_DIGITAL_TWIN = "DTRelationshipTestsRoomTwin"


class DigitalTwinsRelationshipTests(AzureTestCase):

    def _get_client(self, endpoint, **kwargs):
        credential = self.get_credential(DigitalTwinsClient)
        return self.create_client_from_credential(
            DigitalTwinsClient,
            credential,
            endpoint=endpoint,
            **kwargs)

    def _set_up_models(self, client, *models):
        dtdl_model_building = {
            "@id": BUILDING_MODEL_ID,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Building",
            "contents": [
                {
                "@type": "Relationship",
                "name": "has",
                "target": FLOOR_MODEL_ID,
                "properties": [
                    {
                    "@type": "Property",
                    "name": "isAccessRestricted",
                    "schema": "boolean"
                    }
                ]
                },
                {
                "@type": "Property",
                "name": "AverageTemperature",
                "schema": "double"
                }
            ]
        }
        dtdl_model_floor = {
            "@id": FLOOR_MODEL_ID,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Floor",
            "contents": [
                {
                "@type": "Relationship",
                "name": "contains",
                "target": ROOM_MODEL_ID
                },
                {
                "@type": "Property",
                "name": "AverageTemperature",
                "schema": "double"
                }
            ]
        }
        dtdl_model_room = {
            "@id": ROOM_MODEL_ID,
            "@type": "Interface",
            "@context": "dtmi:dtdl:context;2",
            "displayName": "Room",
            "contents": [
                {
                "@type": "Property",
                "name": "Temperature",
                "schema": "double"
                },
                {
                "@type": "Property",
                "name": "IsOccupied",
                "schema": "boolean"
                }
            ]
        }
        try:
            client.create_models([dtdl_model_building, dtdl_model_floor, dtdl_model_room])
        except ResourceExistsError:
            pass
        building_digital_twin = {
            "$metadata": {
                "$model": BUILDING_MODEL_ID
            },
            "AverageTemperature": 68
        }
        client.upsert_digital_twin(BUILDING_DIGITAL_TWIN, building_digital_twin)
        floor_digital_twin = {
            "$metadata": {
                "$model": FLOOR_MODEL_ID
            },
            "AverageTemperature": 75
        }
        client.upsert_digital_twin(FLOOR_DIGITAL_TWIN, floor_digital_twin)
        room_digital_twin = {
            "$metadata": {
                "$model": ROOM_MODEL_ID
            },
            "Temperature": 80,
            "IsOccupied": True
        }
        client.upsert_digital_twin(ROOM_DIGITAL_TWIN, room_digital_twin)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_create_basic_relationship(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        created_relationship = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship)
        assert created_relationship['$relationshipId'] == "FloorContainsRoom"
        assert created_relationship['$etag']

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_create_invalid_relationship(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        with pytest.raises(ResourceNotFoundError):
            client.upsert_relationship(
                "foo",
                "FloorContainsRoom",
                relationship)
        upserted = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "foo",
            relationship)
        assert upserted['$relationshipId'] == 'foo'
        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": "foo"
        }
        with pytest.raises(HttpResponseError):
            client.upsert_relationship(
                FLOOR_DIGITAL_TWIN,
                "FloorContainsRoom",
                relationship)
        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": "foo",
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        upserted = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship)
        assert upserted['$sourceId'] == 'DTRelationshipTestsFloorTwin'
        relationship =   {
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        upserted = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship)
        assert upserted['$sourceId'] == 'DTRelationshipTestsFloorTwin'
        assert upserted['$relationshipId'] == 'FloorContainsRoom'
        relationship =   {
            "$relationshipId": "foo",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        upserted = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship)
        assert upserted['$relationshipId'] == 'FloorContainsRoom'
        relationship =   {
            "$targetId": ROOM_DIGITAL_TWIN
        }
        with pytest.raises(HttpResponseError):
            client.upsert_relationship(
                FLOOR_DIGITAL_TWIN,
                "FloorContainsRoom",
                relationship)
        with pytest.raises(HttpResponseError):
            client.upsert_relationship(
                FLOOR_DIGITAL_TWIN,
                "FloorContainsRoom",
                {})

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_create_relationship_conditionally_if_missing(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        created_relationship = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship)
        assert created_relationship.get('$relationshipId') == "FloorContainsRoom"
        with pytest.raises(ResourceExistsError):
            client.upsert_relationship(
                FLOOR_DIGITAL_TWIN,
                "FloorContainsRoom",
                relationship,
                match_condition=MatchConditions.IfMissing)

    @pytest.mark.skip("Conditional etag does not appear to be supported")
    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_create_relationship_conditionally_if_modified(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)

        relationship =   {
            "$relationshipId": "FloorContainsRoom",
            "$sourceId": FLOOR_DIGITAL_TWIN,
            "$relationshipName": "contains",
            "$targetId": ROOM_DIGITAL_TWIN
        }
        created_relationship = client.upsert_relationship(FLOOR_DIGITAL_TWIN, "FloorContainsRoom", relationship)
        assert created_relationship.get('$relationshipId') == "FloorContainsRoom"

        with pytest.raises(ResourceNotModifiedError):
            client.upsert_relationship(
                FLOOR_DIGITAL_TWIN,
                "FloorContainsRoom",
                relationship,
                match_condition=MatchConditions.IfModified,
                etag=created_relationship.get('$etag'))

        updated = client.upsert_relationship(
            FLOOR_DIGITAL_TWIN,
            "FloorContainsRoom",
            relationship,
            match_condition=MatchConditions.IfModified,
            etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        assert updated['$relationshipId'] == "FloorContainsRoom"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_upsert_relationship(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        created_relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            relationship)
        assert created_relationship['$relationshipId'] == "BuildingHasFloor"
        assert created_relationship['isAccessRestricted'] == False

        relationship["isAccessRestricted"] = True
        upserted_relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            relationship)
        assert upserted_relationship['$relationshipId'] == "BuildingHasFloor"
        assert upserted_relationship['isAccessRestricted'] == True

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_upsert_relationship_invalid_conditions(self, resource_group, location, digitaltwin):
        relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ValueError):
            client.upsert_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                relationship,
                match_condition=MatchConditions.IfMissing,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.upsert_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                relationship,
                match_condition=MatchConditions.IfModified)
        
        with pytest.raises(ValueError):
            client.upsert_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                relationship,
                match_condition=MatchConditions.IfNotModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.upsert_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                relationship,
                match_condition=MatchConditions.IfPresent)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_get_relationship(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        created_relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)

        relationship = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert created_relationship == relationship

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_get_relationship_not_existing(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasRoof")
        with pytest.raises(ResourceNotFoundError):
            client.get_relationship("NotABuilding", "BuildingHasFloor")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_relationship(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)

        deleted = client.delete_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_relationship_not_existing(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.delete_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasRoof")
        with pytest.raises(ResourceNotFoundError):
            client.delete_relationship("NotABuilding", "BuildingHasFloor")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_relationship_conditionally_if_not_modified(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)

        with pytest.raises(ResourceModifiedError):
            client.delete_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')

        deleted = client.delete_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            match_condition=MatchConditions.IfNotModified,
            etag=relationship['$etag'])
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_relationship_conditionally_if_present(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)

        deleted = client.delete_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            match_condition=MatchConditions.IfPresent)
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_delete_relationship_invalid_conditions(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ValueError):
            client.delete_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.delete_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                match_condition=MatchConditions.IfNotModified)
        
        with pytest.raises(ValueError):
            client.delete_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.delete_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                match_condition=MatchConditions.IfMissing)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_replace(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        assert relationship['isAccessRestricted'] == False
        patch = [
            {
                "op": "replace",
                "path": "/isAccessRestricted",
                "value": True
            }
        ]

        update = client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        assert update is None
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert updated['isAccessRestricted'] == True

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_remove(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        assert relationship['isAccessRestricted'] == False
        patch = [
            {
                "op": "remove",
                "path": "/isAccessRestricted",
            }
        ]

        update = client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        assert update is None
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert 'isAccessRestricted' not in updated

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_add(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        assert relationship['isAccessRestricted'] == False

        patch = [
            {
                "op": "add",
                "path": "/isAccessRestricted",
                "value": True
            }
        ]
        update = client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        assert update is None
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert updated['isAccessRestricted'] == True

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_multiple(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        assert relationship['isAccessRestricted'] == False
        patch = [
            {
                "op": "replace",
                "path": "/isAccessRestricted",
                "value": True
            },
            {
                "op": "remove",
                "path": "/isAccessRestricted"
            }
        ]
        update = client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        assert update is None
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert 'isAccessRestricted' not in updated

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_invalid_patch(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)

        patch = [
            {
                "op": "move",
                "path": "/isAccessRestricted"
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)

        patch = [
            {
                "op": "remove",
                "path": "/isAccessDoorRestricted"
            }
        ]
        with pytest.raises(HttpResponseError):
            client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        
        patch = {
            "isAccessRestricted": True
        }
        with pytest.raises(HttpResponseError):
            client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)

        patch = [{}]
        with pytest.raises(HttpResponseError):
            client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)
        
        patch = []
        client.update_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor", patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_conditionally_if_not_modified(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        patch = [
            {
                "op": "replace",
                "path": "/isAccessRestricted",
                "value": True
            }
        ]
        with pytest.raises(ResourceModifiedError):
            client.update_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                patch,
                match_condition=MatchConditions.IfNotModified,
                etag='W/"7e67a355-f19c-4c19-8a10-2d69b2d2253f"')
        client.update_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            patch,
            match_condition=MatchConditions.IfNotModified,
            etag=relationship['$etag'])
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert updated['isAccessRestricted'] == True

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_digitaltwin_conditionally_if_present(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        patch = [
            {
                "op": "replace",
                "path": "/isAccessRestricted",
                "value": True
            }
        ]
        client.update_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            patch,
            match_condition=MatchConditions.IfPresent)
        updated = client.get_relationship(BUILDING_DIGITAL_TWIN, "BuildingHasFloor")
        assert updated['isAccessRestricted'] == True

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_invalid_conditions(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        patch = [
            {
                "op": "replace",
                "path": "/isAccessRestricted",
                "value": True
            }
        ]
        with pytest.raises(ValueError):
            client.update_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                patch,
                match_condition=MatchConditions.IfPresent,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                patch,
                match_condition=MatchConditions.IfNotModified)
        
        with pytest.raises(ValueError):
            client.update_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                patch,
                match_condition=MatchConditions.IfModified,
                etag='etag-value')

        with pytest.raises(ValueError):
            client.update_relationship(
                BUILDING_DIGITAL_TWIN,
                "BuildingHasFloor",
                patch,
                match_condition=MatchConditions.IfMissing)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_update_relationship_not_existing(self, resource_group, location, digitaltwin):
        patch = [
            {
                "op": "replace",
                "path": "/Property1",
                "value": 42
            }
        ]
        client = self._get_client(digitaltwin.host_name)
        with pytest.raises(ResourceNotFoundError):
            client.update_relationship(BUILDING_DIGITAL_TWIN, "foo", patch)
        with pytest.raises(ResourceNotFoundError):
            client.update_relationship("foo", "BuildingHasFloor", patch)

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_list_relationships(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        
        all_relationships = list(client.list_relationships(BUILDING_DIGITAL_TWIN))
        assert relationship in all_relationships
        assert all_relationships[0]['$relationshipId'] == "BuildingHasFloor"

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_list_relationship_by_id(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        
        all_relationships = list(client.list_relationships(BUILDING_DIGITAL_TWIN, relationship_id="BuildingHasFloor"))
        assert len(all_relationships) == 0

    @DigitalTwinsRGPreparer(name_prefix="dttest")
    @DigitalTwinsPreparer(name_prefix="dttest")
    def test_list_incoming_relationships(self, resource_group, location, digitaltwin):
        client = self._get_client(digitaltwin.host_name)
        self._set_up_models(client)
        new_relationship =   {
            "$relationshipId": "BuildingHasFloor",
            "$sourceId": BUILDING_DIGITAL_TWIN,
            "$relationshipName": "has",
            "$targetId": FLOOR_DIGITAL_TWIN,
            "isAccessRestricted": False
        }
        relationship = client.upsert_relationship(
            BUILDING_DIGITAL_TWIN,
            "BuildingHasFloor",
            new_relationship)
        
        all_relationships = list(client.list_incoming_relationships(BUILDING_DIGITAL_TWIN))
        assert relationship not in all_relationships
