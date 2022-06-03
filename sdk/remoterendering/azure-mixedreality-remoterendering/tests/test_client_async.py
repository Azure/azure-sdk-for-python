# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import time
import uuid
import functools
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.mixedreality.remoterendering.aio import RemoteRenderingClient
from azure.mixedreality.remoterendering import (AssetConversionInputSettings,
                                                AssetConversionOutputSettings,
                                                AssetConversionStatus,
                                                RenderingSession,
                                                RenderingSessionSize,
                                                RenderingSessionStatus)


from devtools_testutils import AzureTestCase, PowerShellPreparer

from preparers import RemoteRenderingPreparer
from preparers import RemoteRendererClientPreparer as ClientPreparer

RemoteRendererClientPreparer = functools.partial(ClientPreparer, RemoteRenderingClient)


def create_remote_rendering_client(remoterendering_arr_service_endpoint,
                                   remoterendering_arr_account_id,
                                   remoterendering_arr_account_domain,
                                   remoterendering_arr_account_key):

    key_credential = AzureKeyCredential(remoterendering_arr_account_key)

    client = RemoteRenderingClient(
        endpoint=remoterendering_arr_service_endpoint,
        account_id=remoterendering_arr_account_id,
        account_domain=remoterendering_arr_account_domain,
        credential=key_credential)

    return client


class ClientTests(AzureTestCase):
    def get_var(self, variable_name, default_or_playback_value):
        if self.is_live:
            return os.environ.get(variable_name, default_or_playback_value)

        return default_or_playback_value

    @RemoteRenderingPreparer()
    def test_create_client(self,
                           remoterendering_arr_service_endpoint,
                           remoterendering_arr_account_id,
                           remoterendering_arr_account_domain,
                           remoterendering_arr_account_key):
        client = create_remote_rendering_client(remoterendering_arr_service_endpoint,
                                                remoterendering_arr_account_id,
                                                remoterendering_arr_account_domain,
                                                remoterendering_arr_account_key)

        assert client is not None

    @RemoteRenderingPreparer()
    def test_create_client_with_invalid_arguments(self,
                                                  remoterendering_arr_service_endpoint,
                                                  remoterendering_arr_account_id,
                                                  remoterendering_arr_account_domain,
                                                  remoterendering_arr_account_key):

        key_credential = AzureKeyCredential(remoterendering_arr_account_key)
        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=None,
                account_id=remoterendering_arr_account_id,
                account_domain=remoterendering_arr_account_domain,
                credential=key_credential)

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=remoterendering_arr_service_endpoint,
                account_id=None,
                account_domain=remoterendering_arr_account_domain,
                credential=key_credential)

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=remoterendering_arr_service_endpoint,
                account_id=remoterendering_arr_account_id,
                account_domain=None,
                credential=key_credential)

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=remoterendering_arr_service_endpoint,
                account_id=remoterendering_arr_account_id,
                account_domain=remoterendering_arr_account_domain,
                credential=None)

        with pytest.raises(ValueError):
            RemoteRenderingClient(
                endpoint=remoterendering_arr_service_endpoint,
                account_id=remoterendering_arr_account_id,
                account_domain=remoterendering_arr_account_domain,
                credential=key_credential,
                authentication_endpoint_url="#")

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    async def test_simple_conversion(self,
                                     client,
                                     remoterendering_arr_storage_account_name,
                                     remoterendering_storage_endpoint_suffix,
                                     remoterendering_arr_blob_container_name,
                                     remoterendering_arr_sas_token
                                     ):

        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "1724f808-17c6-4058-93c8-f39c2a84b0b7"

        storage_container_uri = "https://"+remoterendering_arr_storage_account_name + \
            ".blob."+remoterendering_storage_endpoint_suffix+"/"+remoterendering_arr_blob_container_name

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBox.fbx",
            blob_prefix="Input",
            storage_container_read_list_sas="?"+remoterendering_arr_sas_token
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id,
            storage_container_write_sas="?"+remoterendering_arr_sas_token
        )

        conversion_poller = await client.begin_asset_conversion(
            conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
        )

        conversion = await client.get_asset_conversion(conversion_id)
        assert conversion.id == conversion_id
        assert conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert conversion.status != AssetConversionStatus.FAILED

        finished_conversion = await conversion_poller.result()

        assert finished_conversion.id == conversion_id
        assert finished_conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert finished_conversion.status == AssetConversionStatus.SUCCEEDED
        finished_conversion.output.asset_uri.endswith(conversion_id+"/testBox.arrAsset")

        foundConversion = False
        conversions = await client.list_asset_conversions()
        async for c in conversions:
            if(c.id == conversion_id):
                foundConversion = True
                break
        assert foundConversion == True

    @RemoteRenderingPreparer()
    async def test_failed_conversion_unauthorized(self,
                                                  remoterendering_arr_service_endpoint,
                                                  remoterendering_arr_account_id,
                                                  remoterendering_arr_account_domain,
                                                  remoterendering_arr_account_key,
                                                  remoterendering_arr_storage_account_name,
                                                  remoterendering_storage_endpoint_suffix,
                                                  remoterendering_arr_blob_container_name,
                                                  remoterendering_arr_sas_token
                                                  ):
        client = create_remote_rendering_client(remoterendering_arr_service_endpoint,
                                                remoterendering_arr_account_id,
                                                remoterendering_arr_account_domain,
                                                "thisisnotthekey")

        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "1724f808-17c6-4058-93c8-f39c2a84b0b7"

        storage_container_uri = "https://"+remoterendering_arr_storage_account_name + \
            ".blob."+remoterendering_storage_endpoint_suffix+"/"+remoterendering_arr_blob_container_name

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

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    async def test_failed_conversion_no_access(self,
                                               client,
                                               remoterendering_arr_storage_account_name,
                                               remoterendering_storage_endpoint_suffix,
                                               remoterendering_arr_blob_container_name,
                                               remoterendering_arr_sas_token
                                               ):
        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "b994f753-8835-426f-9b04-af990407acca"

        storage_container_uri = "https://"+remoterendering_arr_storage_account_name + \
            ".blob."+remoterendering_storage_endpoint_suffix+"/"+remoterendering_arr_blob_container_name

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

        assert excinfo.value.status_code == 403
        error_details = excinfo.value
        assert "storage" in error_details.message
        assert "permissions" in error_details.message

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    async def test_failed_conversion_missing_asset(self,
                                                   client,
                                                   remoterendering_arr_storage_account_name,
                                                   remoterendering_storage_endpoint_suffix,
                                                   remoterendering_arr_blob_container_name,
                                                   remoterendering_arr_sas_token
                                                   ):
        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "3ff6ab5c-600a-4892-bae9-348f215b1fa4"

        storage_container_uri = "https://"+remoterendering_arr_storage_account_name + \
            ".blob."+remoterendering_storage_endpoint_suffix+"/"+remoterendering_arr_blob_container_name

        input_settings = AssetConversionInputSettings(
            storage_container_uri=storage_container_uri,
            relative_input_asset_path="testBoxWhichDoesNotExist.fbx",
            blob_prefix="Input",
            storage_container_read_list_sas="?"+remoterendering_arr_sas_token
        )
        output_settings = AssetConversionOutputSettings(
            storage_container_uri=storage_container_uri,
            blob_prefix=conversion_id,
            storage_container_write_sas="?"+remoterendering_arr_sas_token
        )
        with pytest.raises(HttpResponseError) as excinfo:
            conversion_poller = await client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )
            await conversion_poller.result()

        error_details = excinfo.value
        assert "invalid input" in error_details.error.message.lower()
        assert "logs" in error_details.error.message.lower()

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    async def test_simple_session(self,
                                  client
                                  ):

        if self.is_live:
            session_id = str(uuid.uuid4())
        else:
            session_id = "f3fd6db9-86c6-4bee-b652-fb1fc0dde08e"

        session_poller = await client.begin_rendering_session(
            session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=15)

        session = await client.get_rendering_session(session_id)
        assert session.id == session_id
        assert session.size == RenderingSessionSize.STANDARD

        assert session.lease_time_minutes == 15
        assert session.status != RenderingSessionStatus.ERROR

        ready_session = await session_poller.result()
        assert ready_session.id == session_id
        assert ready_session.size == RenderingSessionSize.STANDARD
        assert ready_session.lease_time_minutes == 15
        assert ready_session.status == RenderingSessionStatus.READY

        assert ready_session.hostname
        assert ready_session.arr_inspector_port is not None
        assert ready_session.handshake_port is not None

        extended_session = await client.update_rendering_session(session_id=session_id, lease_time_minutes=20)
        assert extended_session.id == session_id
        assert extended_session.size == RenderingSessionSize.STANDARD
        assert extended_session.lease_time_minutes == 15 or extended_session.lease_time_minutes == 20
        assert extended_session.status == RenderingSessionStatus.READY

        foundSession = False
        async for s in await client.list_rendering_sessions():
            if s.id == session_id:
                foundSession = True
                break
        assert foundSession == True

        await client.stop_rendering_session(session_id)
        stopped_session = await client.get_rendering_session(session_id)
        assert stopped_session.status == RenderingSessionStatus.STOPPED

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    async def test_failed_session_request(self,
                                          client
                                          ):
        if self.is_live:
            session_id = str(uuid.uuid4())
        else:
            session_id = "dbab9c99-6971-4fbd-84c3-b00445ec3c04"

        with pytest.raises(HttpResponseError) as excinfo:
            # Make an invalid request (negative lease time).
            session_poller = await client.begin_rendering_session(
                session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=-4)

        assert excinfo.value.status_code == 400
        exception = excinfo.value
        assert "lease" in exception.message.lower()
        assert "negative" in exception.message.lower()
