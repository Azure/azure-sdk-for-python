# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import azure.ai.vision.face.models as models


def _assert_is_string_and_not_empty(val: str):
    assert isinstance(val, str) and bool(val)


def _assert_face_rectangle_not_empty(face_rectangle: models.FaceRectangle):
    assert face_rectangle is not None
    assert face_rectangle.top > 0
    assert face_rectangle.left > 0
    assert face_rectangle.width > 0
    assert face_rectangle.height > 0


def _assert_liveness_outputs_target_not_empty(target: models.LivenessOutputsTarget):
    _assert_face_rectangle_not_empty(target.face_rectangle)
    assert bool(target.file_name)
    assert target.time_offset_within_file >= 0
    assert isinstance(target.image_type, models.FaceImageType)


def _assert_liveness_with_verify_image_not_empty(
    verify_image: models.LivenessWithVerifyImage,
):
    _assert_face_rectangle_not_empty(verify_image.face_rectangle)
    assert isinstance(verify_image.quality_for_recognition, models.QualityForRecognition)


def _assert_liveness_with_verify_outputs_not_empty(
    output: models.LivenessWithVerifyOutputs,
):
    _assert_liveness_with_verify_image_not_empty(output.verify_image)
    assert output.match_confidence > 0
    assert output.is_identical is not None


def _assert_liveness_response_body_not_empty(body: models.LivenessResponseBody, is_liveness_with_verify: bool = True):
    assert body.liveness_decision in models.FaceLivenessDecision
    _assert_liveness_outputs_target_not_empty(body.target)
    assert body.model_version_used in models.LivenessModel
    if is_liveness_with_verify:
        _assert_liveness_with_verify_outputs_not_empty(body.verify_result)


def _assert_session_audit_entry_request_info_not_empty(
    request: models.AuditRequestInfo,
):
    assert bool(request.url)
    assert bool(request.method)
    assert request.content_length > 0
    assert bool(request.content_type)


def _assert_session_audit_entry_response_info_not_empty(
    response: models.AuditLivenessResponseInfo, is_liveness_with_verify: bool = True
):
    _assert_liveness_response_body_not_empty(response.body, is_liveness_with_verify=is_liveness_with_verify)
    assert response.status_code > 0
    assert response.latency_in_milliseconds > 0


def _assert_liveness_session_audit_entry_is_valid(
    audit_entry: models.LivenessSessionAuditEntry,
    expected_session_id="",
    is_liveness_with_verify: bool = True,
):
    assert bool(audit_entry.id)
    assert bool(expected_session_id) or audit_entry.session_id == expected_session_id
    assert bool(audit_entry.request_id)
    assert audit_entry.received_date_time is not None
    _assert_session_audit_entry_request_info_not_empty(audit_entry.request)
    _assert_session_audit_entry_response_info_not_empty(
        audit_entry.response, is_liveness_with_verify=is_liveness_with_verify
    )
    assert bool(audit_entry.digest)
