# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import base64
import os
import tempfile
from pathlib import Path

import pytest

from azure.ai.evaluation._legacy.prompty._utils import _inline_image, _to_content_str_or_list


@pytest.mark.unittest
class TestInlineImageGracefulFallback:
    """Tests for graceful handling of unresolvable relative image paths (ICM 756728740).

    Document Intelligence generates markdown with ![alt text](figures/X.Y) syntax for
    extracted figures. These are relative references meaningful only within Document
    Intelligence's context and are NOT actual files on disk. The evaluation pipeline
    should treat them as plain text instead of crashing.
    """

    def test_unresolvable_relative_path_returns_text(self):
        """Unresolvable relative path like figures/1.1 should return text, not raise."""
        result = _inline_image("![figure](figures/1.1)", Path("/tmp"), "auto")
        assert result["type"] == "text"
        assert result["text"] == "![figure](figures/1.1)"

    def test_unresolvable_relative_path_no_extension(self):
        """Path with no file extension (common in Doc Intelligence output) should return text."""
        result = _inline_image("![alt](some/path/to/image)", Path("/tmp"), "auto")
        assert result["type"] == "text"
        assert result["text"] == "![alt](some/path/to/image)"

    def test_unresolvable_relative_path_with_extension(self):
        """Non-existent path with an image extension should still return text (file doesn't exist)."""
        result = _inline_image("![alt](missing/image.png)", Path("/tmp"), "auto")
        assert result["type"] == "text"
        assert result["text"] == "![alt](missing/image.png)"

    def test_http_url_passthrough(self):
        """HTTP URLs should still be passed through as image_url type."""
        result = _inline_image("![alt](https://example.com/img.png)", Path("/tmp"), "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == "https://example.com/img.png"

    def test_https_url_passthrough(self):
        """HTTPS URLs should still be passed through as image_url type."""
        result = _inline_image("![alt](https://example.com/photo.jpg)", Path("/tmp"), "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == "https://example.com/photo.jpg"

    def test_data_uri_base64_passthrough(self):
        """Data URIs with base64 encoding should still be passed through."""
        data_uri = "![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==)"
        result = _inline_image(data_uri, Path("/tmp"), "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"].startswith("data:image/png;base64,")

    def test_real_local_image_file(self):
        """A real local image file should still be base64-encoded as before."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal valid PNG file (1x1 pixel)
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
                "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
            )
            img_path = Path(tmpdir) / "test_image.png"
            img_path.write_bytes(png_data)

            result = _inline_image(f"![test]({img_path.name})", Path(tmpdir), "auto")
            assert result["type"] == "image_url"
            assert result["image_url"]["url"].startswith("data:")
            assert "base64" in result["image_url"]["url"]


@pytest.mark.unittest
class TestToContentStrOrListGracefulFallback:
    """Tests for _to_content_str_or_list handling of unresolvable image paths."""

    def test_text_with_unresolvable_image_ref(self):
        """Mixed text with unresolvable image ref should not crash."""
        result = _to_content_str_or_list(
            "Some text ![fig](figures/1.1) more text", Path("/tmp"), "auto"
        )
        # Should return a list with text chunks (no crash)
        assert isinstance(result, list)
        # All chunks should be of type "text" since the image is unresolvable
        for item in result:
            assert item["type"] == "text"

    def test_plain_text_no_images(self):
        """Plain text with no image references should return a string."""
        result = _to_content_str_or_list("Just plain text", Path("/tmp"), "auto")
        assert isinstance(result, str)
        assert result == "Just plain text"

    def test_text_with_http_image(self):
        """Text with valid HTTP image URL should return list with image_url type."""
        result = _to_content_str_or_list(
            "Before ![alt](https://example.com/img.png) after", Path("/tmp"), "auto"
        )
        assert isinstance(result, list)
        image_items = [item for item in result if item["type"] == "image_url"]
        assert len(image_items) == 1
        assert image_items[0]["image_url"]["url"] == "https://example.com/img.png"

    def test_multiple_unresolvable_refs(self):
        """Multiple unresolvable image refs in one string should all become text."""
        result = _to_content_str_or_list(
            "Text ![a](figures/1.1) middle ![b](figures/2.3) end", Path("/tmp"), "auto"
        )
        assert isinstance(result, list)
        for item in result:
            assert item["type"] == "text"

    def test_real_local_image_in_mixed_content(self):
        """Real local image file mixed with text should work as before."""
        with tempfile.TemporaryDirectory() as tmpdir:
            png_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
                "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
            )
            img_path = Path(tmpdir) / "real.png"
            img_path.write_bytes(png_data)

            result = _to_content_str_or_list(
                f"Before ![img]({img_path.name}) after", Path(tmpdir), "auto"
            )
            assert isinstance(result, list)
            image_items = [item for item in result if item["type"] == "image_url"]
            assert len(image_items) == 1
            assert image_items[0]["image_url"]["url"].startswith("data:")
