# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import uuid

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.vision.face.models import (
    CreateLivenessSessionContent,
    FaceSessionStatus,
    LivenessOperationMode,
)

from preparers import FaceSessionClientPreparer, FacePreparer
from _shared.asserter import (
    _assert_is_string_and_not_empty,
    _assert_liveness_session_audit_entry_is_valid,
    _assert_liveness_with_verify_image_not_empty,
)
from _shared import helpers
from _shared.constants import TestImages


class TestLivenessWithVerifySession(AzureRecordedTestCase):
    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_create_session(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_id = variables.setdefault("deviceCorrelationId", str(uuid.uuid4()))

        # Test `create session` operation
        created_session = client.create_liveness_with_verify_session(
            CreateLivenessSessionContent(
                liveness_operation_mode=LivenessOperationMode.PASSIVE,
                device_correlation_id=recorded_device_correlation_id),
            None)  # verify_image = None

        _assert_is_string_and_not_empty(created_session.session_id)
        _assert_is_string_and_not_empty(created_session.auth_token)
        session_id = created_session.session_id

        session = client.get_liveness_with_verify_session_result(session_id)
        assert session.device_correlation_id == recorded_device_correlation_id

        # Teardown
        client.delete_liveness_with_verify_session(session_id)

        return variables

    @pytest.mark.live_test_only  # It's hard to sanitize the multipart form-data request.
    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_create_session_with_verify_image(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_id = variables.setdefault("deviceCorrelationId", str(uuid.uuid4()))

        # verify_image
        sample_file_path = helpers.get_image_path(TestImages.IMAGE_DETECTION_1)

        # Test `create session` operation
        created_session = client.create_liveness_with_verify_session(
            CreateLivenessSessionContent(
                liveness_operation_mode=LivenessOperationMode.PASSIVE,
                device_correlation_id=recorded_device_correlation_id),
            verify_image=helpers.read_file_content(sample_file_path))

        _assert_is_string_and_not_empty(created_session.session_id)
        _assert_is_string_and_not_empty(created_session.auth_token)
        _assert_liveness_with_verify_image_not_empty(created_session.verify_image)

        session_id = created_session.session_id

        session = client.get_liveness_with_verify_session_result(session_id)
        assert session.device_correlation_id == recorded_device_correlation_id

        # Teardown
        client.delete_liveness_with_verify_session(session_id)

        return variables

    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_list_sessions(self, client, **kwargs):
        variables = kwargs.pop("variables", {})

        # key-value pairs = {device_correlation_id, created_session_id}
        recorded_device_correlation_ids_dict = {
            variables.setdefault("deviceCorrelationId1", str(uuid.uuid4())): "",  # '{id1}': ""
            variables.setdefault("deviceCorrelationId2", str(uuid.uuid4())): "",  # '{id2}': ""
        }

        # Create 2 sessions with different deivce_correlation_id
        for dcid in recorded_device_correlation_ids_dict.keys():
            created_session = client.create_liveness_with_verify_session(
                CreateLivenessSessionContent(
                    liveness_operation_mode=LivenessOperationMode.PASSIVE,
                    device_correlation_id=dcid),
                None)  # verify_image = None

            _assert_is_string_and_not_empty(created_session.session_id)
            recorded_device_correlation_ids_dict[dcid] = created_session.session_id

        # Test `list sessions` operation
        result = client.get_liveness_with_verify_sessions()

        assert len(result) == 2
        assert result[0].id < result[1].id
        for session in result:
            assert session.device_correlation_id in recorded_device_correlation_ids_dict
            assert session.id == recorded_device_correlation_ids_dict[session.device_correlation_id]
            assert session.created_date_time is not None
            assert session.auth_token_time_to_live_in_seconds >= 60
            assert session.auth_token_time_to_live_in_seconds <= 86400

        # Teardown
        for sid in recorded_device_correlation_ids_dict.values():
            client.delete_liveness_with_verify_session(sid)

        return variables

    @pytest.mark.playback_test_only
    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_get_session_result(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_session_id = variables.setdefault("sessionId", "1b79f44d-d8e0-4652-8f2d-637c4205d854")

        session = client.get_liveness_with_verify_session_result(recorded_session_id)
        assert session.id == recorded_session_id
        assert session.created_date_time is not None
        assert session.session_start_date_time is not None
        assert isinstance(session.session_expired, bool)
        _assert_is_string_and_not_empty(session.device_correlation_id)
        assert session.auth_token_time_to_live_in_seconds >= 60
        assert session.auth_token_time_to_live_in_seconds <= 86400
        assert isinstance(session.status, FaceSessionStatus)
        _assert_liveness_session_audit_entry_is_valid(
               session.result, expected_session_id=recorded_session_id, is_liveness_with_verify=False)

        return variables

    @pytest.mark.playback_test_only
    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_get_session_audit_entries(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_session_id = variables.setdefault("sessionId", "1b79f44d-d8e0-4652-8f2d-637c4205d854")

        entries = client.get_liveness_with_verify_session_audit_entries(recorded_session_id)
        assert len(entries) == 2
        for entry in entries:
            _assert_liveness_session_audit_entry_is_valid(
                    entry, expected_session_id=recorded_session_id, is_liveness_with_verify=True)

        return variables

    @FacePreparer()
    @FaceSessionClientPreparer()
    @recorded_by_proxy
    def test_delete_session(self, client, **kwargs):
        variables = kwargs.pop("variables", {})
        recorded_device_correlation_id = variables.setdefault("deviceCorrelationId", str(uuid.uuid4()))

        created_session = client.create_liveness_with_verify_session(
            CreateLivenessSessionContent(
                liveness_operation_mode=LivenessOperationMode.PASSIVE,
                device_correlation_id=recorded_device_correlation_id),
            None)  # verify_image = None
        session_id = created_session.session_id
        _assert_is_string_and_not_empty(session_id)

        # Test `delete session` operation
        client.delete_liveness_with_verify_session(session_id)

        with pytest.raises(ResourceNotFoundError) as exception:
            client.get_liveness_with_verify_session_result(session_id)
        assert exception.value.status_code == 404
        assert exception.value.error.code == "SessionNotFound"

        return variables
