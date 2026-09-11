# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy

from azure.ai.contentsafety.models import (
    DetectOutcome,
    DetectProvenanceOptions,
    DetectedProvenanceType,
    ProvenanceContent,
)
from test_case import ContentSafetyTest, ContentSafetyPreparer


class TestContentProvenanceCase(ContentSafetyTest):
    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_detect_provenance_detected(
        self, content_safety_endpoint, content_safety_key, content_safety_signed_media_uri
    ):
        client = self.create_content_provenance_client_from_key(content_safety_endpoint, content_safety_key)

        result = client.begin_detect(
            DetectProvenanceOptions(content=ProvenanceContent(uri=content_safety_signed_media_uri))
        ).result()

        assert result.outcome == DetectOutcome.PROVENANCE_DETECTED
        assert result.results
        detected_types = {detected.type for detected in result.results}
        assert detected_types <= {DetectedProvenanceType.C2_PA, DetectedProvenanceType.WATERMARK}
        for detected in result.results:
            assert detected.provider
            assert detected.model_name

    @ContentSafetyPreparer()
    @recorded_by_proxy
    def test_detect_provenance_not_detected(
        self, content_safety_endpoint, content_safety_key, content_safety_unsigned_media_uri
    ):
        client = self.create_content_provenance_client_from_key(content_safety_endpoint, content_safety_key)

        result = client.begin_detect(
            DetectProvenanceOptions(content=ProvenanceContent(uri=content_safety_unsigned_media_uri))
        ).result()

        assert result.outcome == DetectOutcome.NO_PROVENANCE_DETECTED
        assert not result.results
