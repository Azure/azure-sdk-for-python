# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import uuid

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.mixedreality.remoterendering.aio import RemoteRenderingClient
from azure.mixedreality.remoterendering import (
    AssetConversionInputSettings,
    AssetConversionOutputSettings,
    AssetConversionStatus,
    RenderingSessionSize,
    RenderingSessionStatus
)
from devtools_testutils import AzureRecordedTestCase


class TestRemoteRenderingClientAsync(AzureRecordedTestCase):

    def test_create_client(self, account_info):

        client = RemoteRenderingClient(
            endpoint=account_info["service_endpoint"],
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=account_info["key_credential"]
        )
        assert client is not None

    def test_create_client_with_invalid_arguments(self, account_info):
        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=None,
                account_id=account_info["account_id"],
                account_domain=account_info["account_domain"],
                credential=account_info["key_credential"])

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=account_info["service_endpoint"],
                account_id=None,
                account_domain=account_info["account_domain"],
                credential=account_info["key_credential"])

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=account_info["service_endpoint"],
                account_id=account_info["account_id"],
                account_domain=None,
                credential=account_info["key_credential"])

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=account_info["service_endpoint"],
                account_id=account_info["account_id"],
                account_domain=account_info["account_domain"],
                credential=None)

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=account_info["service_endpoint"],
                account_id=account_info["account_id"],
                account_domain=account_info["account_domain"],
                credential=account_info["key_credential"],
                authentication_endpoint_url="#")

    @pytest.mark.asyncio
    async def test_simple_conversion(self, recorded_test, account_info, async_arr_client):
        conversion_id = account_info["id_placeholder"]
        if self.is_live:
            conversion_id += str(uuid.uuid4())

        storage_container_uri = "https://"+account_info["storage_account_name"] + \
            ".blob."+account_info["storage_endpoint_suffix"]+"/"+account_info["blob_container_name"]

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBox.fbx",
            blob_prefix="Input",
            storage_container_read_list_sas="?"+account_info["sas_token"]
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id,
            storage_container_write_sas="?"+account_info["sas_token"]
        )

        conversion_poller = await async_arr_client.begin_asset_conversion(
            conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
        )

        conversion = await async_arr_client.get_asset_conversion(conversion_id)
        assert conversion.id == conversion_id
        assert conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert conversion.status != AssetConversionStatus.FAILED

        finished_conversion = await conversion_poller.result()

        assert finished_conversion.id == conversion_id
        assert finished_conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert finished_conversion.status == AssetConversionStatus.SUCCEEDED
        finished_conversion.output.asset_uri.endswith(conversion_id+"/testBox.arrAsset")

        foundConversion = False
        conversions = await async_arr_client.list_asset_conversions()
        async for c in conversions:
            if(c.id == conversion_id):
                foundConversion = True
                break
        assert foundConversion == True

    @pytest.mark.asyncio
    async def test_failed_conversion_unauthorized(self, recorded_test, account_info):
        client = RemoteRenderingClient(
            endpoint=account_info["service_endpoint"],
            account_id=account_info["account_id"],
            account_domain=account_info["account_domain"],
            credential=AzureKeyCredential("wrong_key")
        )

        conversion_id = account_info["id_placeholder"]
        if self.is_live:
            conversion_id += str(uuid.uuid4())

        storage_container_uri = "https://"+account_info["storage_account_name"] + \
            ".blob."+account_info["storage_endpoint_suffix"]+"/"+account_info["blob_container_name"]

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBox.fbx",
            blob_prefix="Input"
            # Do not provide SAS access to the container, and assume the test account is not linked to the storage.
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id
            # Do not provide SAS access to the container, and assume the test account is not linked to the storage.
        )

        with pytest.raises(HttpResponseError) as excinfo:
            # make the request which cannot access the storage account
            conversion_poller = await client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )

        exception = excinfo.value
        assert exception.status_code == 401
        assert "Unauthorized" in exception.message

    @pytest.mark.asyncio
    async def test_failed_conversion_no_access(self, recorded_test, account_info, async_arr_client):
        conversion_id = account_info["id_placeholder"]
        if self.is_live:
            conversion_id += str(uuid.uuid4())

        storage_container_uri = "https://"+account_info["storage_account_name"] + \
            ".blob."+account_info["storage_endpoint_suffix"]+"/"+account_info["blob_container_name"]

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBox.fbx",
            blob_prefix="Input"
            # Do not provide SAS access to the container, and assume the test account is not linked to the storage.
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id
            # Do not provide SAS access to the container, and assume the test account is not linked to the storage.
        )

        with pytest.raises(HttpResponseError) as excinfo:
            # make the request which cannot access the storage account
            conversion_poller = await async_arr_client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )

        assert excinfo.value.status_code == 403
        error_details = excinfo.value
        assert "storage" in error_details.message
        assert "permissions" in error_details.message

    @pytest.mark.asyncio
    async def test_failed_conversion_missing_asset(self, recorded_test, account_info, async_arr_client):
        conversion_id = account_info["id_placeholder"]
        if self.is_live:
            conversion_id += str(uuid.uuid4())

        storage_container_uri = "https://"+account_info["storage_account_name"] + \
            ".blob."+account_info["storage_endpoint_suffix"]+"/"+account_info["blob_container_name"]

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBoxWhichDoesNotExist.fbx",
            blob_prefix="Input",
            storage_container_read_list_sas="?"+account_info["sas_token"]
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id,
            storage_container_write_sas="?"+account_info["sas_token"]
        )
        with pytest.raises(HttpResponseError) as excinfo:
            conversion_poller = await async_arr_client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )
            await conversion_poller.result()

        error_details = excinfo.value
        assert "InputContainerError" == error_details.error.code
        # Message: "Could not find the asset file in the storage account. Please make sure all paths and names are correct and the file is uploaded to storage."
        assert error_details.error.message is not None
        assert "Could not find the asset file in the storage account" in error_details.error.message

    @pytest.mark.asyncio
    async def test_simple_session(self, recorded_test, account_info, async_arr_client):
        session_id = account_info["id_placeholder"]
        if self.is_live:
            session_id += str(uuid.uuid4())

        session_poller = await async_arr_client.begin_rendering_session(
            session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=15)

        session = await async_arr_client.get_rendering_session(session_id)
        assert session.id == session_id

        assert session.lease_time_minutes == 15
        assert session.status != RenderingSessionStatus.ERROR

        ready_session = await session_poller.result()
        assert ready_session.id == session_id
        assert ready_session.lease_time_minutes == 15
        assert ready_session.status == RenderingSessionStatus.READY

        assert ready_session.hostname
        assert ready_session.arr_inspector_port is not None
        assert ready_session.handshake_port is not None

        extended_session = await async_arr_client.update_rendering_session(session_id=session_id, lease_time_minutes=20)
        assert extended_session.id == session_id
        assert extended_session.lease_time_minutes == 15 or extended_session.lease_time_minutes == 20
        assert extended_session.status == RenderingSessionStatus.READY

        foundSession = False
        async for s in await async_arr_client.list_rendering_sessions():
            if s.id == session_id:
                foundSession = True
                break
        assert foundSession == True

        await async_arr_client.stop_rendering_session(session_id)
        stopped_session = await async_arr_client.get_rendering_session(session_id)
        assert stopped_session.status == RenderingSessionStatus.STOPPED

    @pytest.mark.asyncio
    async def test_failed_session_request(self, recorded_test, account_info, async_arr_client):
        session_id = account_info["id_placeholder"]
        if self.is_live:
            session_id += str(uuid.uuid4())

        with pytest.raises(HttpResponseError) as excinfo:
            # Make an invalid request (negative lease time).
            session_poller = await async_arr_client.begin_rendering_session(
                session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=-4)

        assert excinfo.value.status_code == 400
        exception = excinfo.value
        assert "lease" in exception.message.lower()
        assert "negative" in exception.message.lower()
