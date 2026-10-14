# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Offline deserialization tests for AnalysisResult.infos."""

from __future__ import annotations

from azure.ai.contentunderstanding.models import AnalysisResult


def test_deserialize_infos_from_invoice_like_payload() -> None:
    """Invoice-like payloads expose infos with LLMStats diagnostics."""
    result = AnalysisResult(
        {
            "analyzerId": "prebuilt-invoice",
            "apiVersion": "2026-06-01-preview",
            "contents": [],
            "infos": [
                {
                    "code": "LLMStats",
                    "message": "completion calls: 2; embedding calls: 1; completion latency: 1.2s",
                }
            ],
        }
    )

    assert result.infos is not None
    assert len(result.infos) == 1
    assert result.infos[0].code == "LLMStats"
    assert "completion calls" in (result.infos[0].message or "")


def test_deserialize_missing_infos() -> None:
    """Missing infos deserializes as None (optional field contract)."""
    result = AnalysisResult(
        {
            "analyzerId": "prebuilt-layout",
            "apiVersion": "2026-06-01-preview",
            "contents": [],
        }
    )

    # Document actual contract: optional field is None when absent from payload.
    assert result.infos is None or result.infos == []
