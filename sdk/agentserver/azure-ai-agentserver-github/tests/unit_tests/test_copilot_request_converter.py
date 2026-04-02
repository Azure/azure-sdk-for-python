# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# ---------------------------------------------------------
"""Unit tests for CopilotRequestConverter.

Tests cover prompt extraction from various input shapes and
attachment materialization from base64 content parts.
"""

import base64
import os
import pytest

from azure.ai.agentserver.core.models import CreateResponse
from azure.ai.agentserver.github._copilot_request_converter import (
    CopilotRequestConverter,
    ConvertedAttachments,
)


# ---------------------------------------------------------------------------
# convert() — prompt extraction
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConvertPrompt:
    """Tests for CopilotRequestConverter.convert() prompt extraction."""

    def test_string_input(self):
        """Plain string input is returned as-is."""
        request = CreateResponse(input="hello world")
        converter = CopilotRequestConverter(request)
        assert converter.convert() == "hello world"

    def test_empty_input(self):
        """Missing input returns empty string."""
        request = CreateResponse(input=None)
        converter = CopilotRequestConverter(request)
        assert converter.convert() == ""

    def test_message_list_with_text_content(self):
        """List of messages with text content parts."""
        request = CreateResponse(input=[
            {"content": [{"type": "input_text", "text": "first message"}]},
            {"content": [{"type": "input_text", "text": "second message"}]},
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert()
        assert "first message" in result
        assert "second message" in result

    def test_message_with_string_content(self):
        """Message with plain string content (not a list)."""
        request = CreateResponse(input=[
            {"content": "simple text"},
        ])
        converter = CopilotRequestConverter(request)
        assert converter.convert() == "simple text"

    def test_implicit_user_message(self):
        """Dict with content key treated as single message."""
        request = CreateResponse(input={"content": "implicit message"})
        converter = CopilotRequestConverter(request)
        assert converter.convert() == "implicit message"

    def test_image_url_annotation(self):
        """External image URLs are included as annotations in the prompt."""
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_text", "text": "look at this"},
                    {
                        "type": "input_image",
                        "image_url": {"url": "https://example.com/photo.jpg"},
                    },
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert()
        assert "look at this" in result
        assert "[image: https://example.com/photo.jpg]" in result

    def test_data_uri_image_not_in_prompt(self):
        """Base64 data URI images are NOT included in the prompt text (handled as attachments)."""
        data_uri = "data:image/png;base64,iVBORw0KGgo="
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_text", "text": "see this"},
                    {"type": "input_image", "image_url": {"url": data_uri}},
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert()
        assert "see this" in result
        assert "data:" not in result

    def test_file_without_data_annotated(self):
        """File with only file_id (no file_data) is annotated in the prompt."""
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_file", "file_id": "file_abc123", "filename": "report.pdf"},
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert()
        assert "[file: report.pdf]" in result


# ---------------------------------------------------------------------------
# convert_attachments() — file materialization
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConvertAttachments:
    """Tests for CopilotRequestConverter.convert_attachments()."""

    def test_no_attachments(self):
        """String input produces no attachments."""
        request = CreateResponse(input="just text")
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        assert isinstance(result, ConvertedAttachments)
        assert not result  # bool(ConvertedAttachments) is False when empty

    def test_base64_file_attachment(self):
        """Base64 file_data is materialized to a temp file."""
        content = b"hello world"
        b64 = base64.b64encode(content).decode()
        request = CreateResponse(input=[
            {
                "content": [
                    {
                        "type": "input_file",
                        "file_data": b64,
                        "filename": "test.txt",
                    },
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        try:
            assert result  # has attachments
            assert len(result.attachments) == 1
            att = result.attachments[0]
            assert att["type"] == "file"
            assert att["displayName"] == "test.txt"
            # Verify temp file exists and has correct content
            assert os.path.exists(att["path"])
            with open(att["path"], "rb") as f:
                assert f.read() == content
        finally:
            result.cleanup()

    def test_base64_image_attachment(self):
        """Base64 data URI image is materialized to a temp file."""
        # Minimal valid PNG (1x1 pixel)
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        b64 = base64.b64encode(png_bytes).decode()
        data_uri = f"data:image/png;base64,{b64}"
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_image", "image_url": {"url": data_uri}},
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        try:
            assert result
            assert len(result.attachments) == 1
            att = result.attachments[0]
            assert att["type"] == "file"
            assert att["path"].endswith(".png")
            assert os.path.exists(att["path"])
            with open(att["path"], "rb") as f:
                assert f.read() == png_bytes
        finally:
            result.cleanup()

    def test_cleanup_removes_temp_files(self):
        """cleanup() deletes all temp files."""
        content = b"temporary data"
        b64 = base64.b64encode(content).decode()
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_file", "file_data": b64, "filename": "tmp.bin"},
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        paths = [att["path"] for att in result.attachments]
        assert all(os.path.exists(p) for p in paths)
        result.cleanup()
        assert all(not os.path.exists(p) for p in paths)

    def test_external_url_image_not_materialized(self):
        """External HTTP image URLs are NOT materialized as attachments."""
        request = CreateResponse(input=[
            {
                "content": [
                    {
                        "type": "input_image",
                        "image_url": {"url": "https://example.com/photo.jpg"},
                    },
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        assert not result  # no attachments

    def test_file_id_only_not_materialized(self):
        """File with only file_id (no file_data) is NOT materialized."""
        request = CreateResponse(input=[
            {
                "content": [
                    {"type": "input_file", "file_id": "file_abc", "filename": "doc.pdf"},
                ]
            },
        ])
        converter = CopilotRequestConverter(request)
        result = converter.convert_attachments()
        assert not result
