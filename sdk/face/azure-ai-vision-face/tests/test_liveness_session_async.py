# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import deque
import pytest
import uuid

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.vision.face.models import (
    CreateLivenessSessionContent,
    FaceSessionStatus,
    LivenessOperationMode,
)

from preparers import AsyncFaceSessionClientPreparer, FacePreparer
from _shared.asserter import (
    _assert_is_string_and_not_empty,
    _assert_liveness_session_audit_entry_is_valid,
)


class TestLivenessSessionAsync(AzureRecordedTestCase):
    @FacePreparer()
    @AsyncFaceSessionClientPreparer()
    @recorded_by_proxy_async
    async def test_create_session(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_id = variables.setdefault("deviceCorrelationId", str(uuid.uuid4()))

        # Test `create session` operation
        created_session = await client.create_liveness_session(
            CreateLivenessSessionContent(
                liveness_operation_mode=LivenessOperationMode.PASSIVE,
                device_correlation_id=recorded_device_correlation_id,
            )
        )

        _assert_is_string_and_not_empty(created_session.session_id)
        _assert_is_string_and_not_empty(created_session.auth_token)
        session_id = created_session.session_id

        session = await client.get_liveness_session_result(session_id)
        assert session.device_correlation_id == recorded_device_correlation_id

        # Teardown
        await client.delete_liveness_session(session_id)
        await client.close()

        return variables

    @FacePreparer()
    @AsyncFaceSessionClientPreparer()
    @recorded_by_proxy_async
    async def test_list_sessions(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_ids = {
            variables.setdefault("deviceCorrelationId1", str(uuid.uuid4())),
            variables.setdefault("deviceCorrelationId2", str(uuid.uuid4())),
        }

        # key = session_id, value = device_correlation_id
        created_session_dict = {}

        # Create 2 sessions with different device_correlation_id
        for dcid in recorded_device_correlation_ids:
            created_session = await client.create_liveness_session(
                CreateLivenessSessionContent(
                    liveness_operation_mode=LivenessOperationMode.PASSIVE,
                    device_correlation_id=dcid,
                )
            )

            _assert_is_string_and_not_empty(created_session.session_id)
            created_session_dict[created_session.session_id] = dcid

        # Sort the dict by key because the `list sessions` operation returns sessions in ascending alphabetical order.
        expected_dcid_queue = deque(value for _, value in sorted(created_session_dict.items(), key=lambda t: t[0]))

        # Test `list sessions` operation
        result = await client.get_liveness_sessions()

        assert len(result) == 2
        for session in result:
            assert session.device_correlation_id == expected_dcid_queue.popleft()
            assert session.created_date_time is not None
            assert session.auth_token_time_to_live_in_seconds >= 60
            assert session.auth_token_time_to_live_in_seconds <= 86400

        # Teardown
        for sid in created_session_dict.keys():
            await client.delete_liveness_session(sid)
        await client.close()

        return variables

    @pytest.mark.playback_test_only
    @FacePreparer()
    @AsyncFaceSessionClientPreparer()
    @recorded_by_proxy_async
    async def test_get_session_result(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_session_id = variables.setdefault("sessionId", "5f8e0996-4ef0-4142-9b5d-e42fa5748a7e")

        session = await client.get_liveness_session_result(recorded_session_id)
        assert session.created_date_time is not None
        assert session.session_start_date_time is not None
        assert isinstance(session.session_expired, bool)
        _assert_is_string_and_not_empty(session.device_correlation_id)
        assert session.auth_token_time_to_live_in_seconds >= 60
        assert session.auth_token_time_to_live_in_seconds <= 86400
        assert isinstance(session.status, FaceSessionStatus)
        _assert_liveness_session_audit_entry_is_valid(
            session.result,
            expected_session_id=recorded_session_id,
            is_liveness_with_verify=False,
        )
        await client.close()

        return variables

    @pytest.mark.playback_test_only
    @FacePreparer()
    @AsyncFaceSessionClientPreparer()
    @recorded_by_proxy_async
    async def test_get_session_audit_entries(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_session_id = variables.setdefault("sessionId", "5f8e0996-4ef0-4142-9b5d-e42fa5748a7e")

        entries = await client.get_liveness_session_audit_entries(recorded_session_id)
        assert len(entries) == 2
        for entry in entries:
            _assert_liveness_session_audit_entry_is_valid(
                entry,
                expected_session_id=recorded_session_id,
                is_liveness_with_verify=False,
            )
        await client.close()

        return variables

    @FacePreparer()
    @AsyncFaceSessionClientPreparer()
    @recorded_by_proxy_async
    async def test_delete_session(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_id = variables.setdefault("deviceCorrelationId", str(uuid.uuid4()))

        created_session = await client.create_liveness_session(
            CreateLivenessSessionContent(
                liveness_operation_mode=LivenessOperationMode.PASSIVE,
                device_correlation_id=recorded_device_correlation_id,
            )
        )
        session_id = created_session.session_id
        _assert_is_string_and_not_empty(session_id)

        # Test `delete session` operation
        await client.delete_liveness_session(session_id)

        with pytest.raises(ResourceNotFoundError) as exception:
            await client.get_liveness_session_result(session_id)
        assert exception.value.status_code == 404
        assert exception.value.error.code == "SessionNotFound"
        await client.close()

        return variables
