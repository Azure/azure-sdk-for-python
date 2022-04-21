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
from azure.mixedreality.remoterendering import (AssetConversionInputSettings,
                                                AssetConversionOutputSettings,
                                                AssetConversionStatus,
                                                RemoteRenderingClient,
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
    def test_simple_conversion(self,
                               client,
                               remoterendering_arr_storage_account_name,
                               remoterendering_storage_endpoint_suffix,
                               remoterendering_arr_blob_container_name,
                               remoterendering_arr_sas_token
                               ):

        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "11b5d55d-b228-4291-8883-df3865a32088"

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

        conversion_poller = client.begin_asset_conversion(
            conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
        )

        conversion = client.get_asset_conversion(conversion_id)
        assert conversion.id == conversion_id
        assert conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert conversion.status != AssetConversionStatus.FAILED

        finished_conversion = conversion_poller.result()

        assert finished_conversion.id == conversion_id
        assert finished_conversion.settings.input_settings.relative_input_asset_path == input_settings.relative_input_asset_path
        assert finished_conversion.status == AssetConversionStatus.SUCCEEDED
        finished_conversion.output.asset_uri.endswith(conversion_id+"/testBox.arrAsset")

        foundConversion = False
        conversions = client.list_asset_conversions()
        for c in conversions:
            if(c.id == conversion_id):
                foundConversion = True
                break
        assert foundConversion == True

    @RemoteRenderingPreparer()
    def test_failed_conversion_unauthorized(self,
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
            conversion_id = "c228b814-e29a-4389-be1c-96e7c0ea668d"

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
            conversion_poller = client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )

        exception = excinfo.value
        assert exception.status_code == 401
        assert "Unauthorized" in exception.message

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    def test_failed_conversion_no_access(self,
                                         client,
                                         remoterendering_arr_storage_account_name,
                                         remoterendering_storage_endpoint_suffix,
                                         remoterendering_arr_blob_container_name,
                                         remoterendering_arr_sas_token
                                         ):

        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "b3bea9f9-db26-45af-a4a1-dc007c1c2ce9"

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
            conversion_poller = client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings
            )

        assert excinfo.value.status_code == 403
        error_details = excinfo.value
        assert "storage" in error_details.message
        assert "permissions" in error_details.message

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    def test_failed_conversion_missing_asset(self,
                                             client,
                                             remoterendering_arr_storage_account_name,
                                             remoterendering_storage_endpoint_suffix,
                                             remoterendering_arr_blob_container_name,
                                             remoterendering_arr_sas_token
                                             ):

        if self.is_live:
            conversion_id = str(uuid.uuid4())
        else:
            conversion_id = "5147aa0f-485a-429f-8d04-bd0b2458cf79"

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
            # make the request which fails in polling because of the missing asset
            conversion_poller = client.begin_asset_conversion(
                conversion_id=conversion_id,  input_settings=input_settings, output_settings=output_settings)
            conversion_poller.result()

        error_details = excinfo.value
        assert "invalid input" in error_details.error.message.lower()
        assert "logs" in error_details.error.message.lower()

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    def test_simple_session(self,
                            client
                            ):
        if self.is_live:
            session_id = str(uuid.uuid4())
        else:
            session_id = "dcb143c5-31c7-4eba-9a9d-d878444de6e0"

        session_poller = client.begin_rendering_session(
            session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=15)

        session = client.get_rendering_session(session_id)
        assert session.id == session_id
        assert session.size == RenderingSessionSize.STANDARD

        assert session.lease_time_minutes == 15
        assert session.status != RenderingSessionStatus.ERROR

        ready_session = session_poller.result()
        assert ready_session.id == session_id
        assert ready_session.size == RenderingSessionSize.STANDARD
        assert ready_session.lease_time_minutes == 15
        assert ready_session.status == RenderingSessionStatus.READY

        assert ready_session.hostname
        assert ready_session.arr_inspector_port is not None
        assert ready_session.handshake_port is not None

        extended_session = client.update_rendering_session(session_id=session_id,  lease_time_minutes=20)
        assert extended_session.id == session_id
        assert extended_session.size == RenderingSessionSize.STANDARD
        assert extended_session.lease_time_minutes == 15 or extended_session.lease_time_minutes == 20
        assert extended_session.status == RenderingSessionStatus.READY

        foundSession = False
        for s in client.list_rendering_sessions():
            if s.id == session_id:
                foundSession = True
                break
        assert foundSession == True

        client.stop_rendering_session(session_id)
        stopped_session = client.get_rendering_session(session_id)
        assert stopped_session.status == RenderingSessionStatus.STOPPED

    @RemoteRenderingPreparer()
    @RemoteRendererClientPreparer()
    def test_failed_session_request(self,
                                    client
                                    ):
        if self.is_live:
            session_id = str(uuid.uuid4())
        else:
            session_id = "8240a701-54f5-4094-9bd4-652e714cb1ad"

        with pytest.raises(HttpResponseError) as excinfo:
            # Make an invalid request (negative lease time).
            session_poller = client.begin_rendering_session(
                session_id=session_id, size=RenderingSessionSize.STANDARD, lease_time_minutes=-4)

        assert excinfo.value.status_code == 400
        exception = excinfo.value
        assert "lease" in exception.message.lower()
        assert "negative" in exception.message.lower()
