# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import base64
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

    def test_unresolvable_relative_path_returns_text(self, tmp_path):
        """Unresolvable relative path like figures/1.1 should return text, not raise."""
        result = _inline_image("![figure](figures/1.1)", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == "![figure](figures/1.1)"

    def test_unresolvable_relative_path_no_extension(self, tmp_path):
        """Path with no file extension (common in Doc Intelligence output) should return text."""
        result = _inline_image("![alt](some/path/to/image)", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == "![alt](some/path/to/image)"

    def test_unresolvable_relative_path_with_extension(self, tmp_path):
        """Non-existent path with an image extension should still return text (file doesn't exist)."""
        result = _inline_image("![alt](missing/image.png)", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == "![alt](missing/image.png)"

    def test_http_url_passthrough(self, tmp_path):
        """HTTP URLs should still be passed through as image_url type."""
        result = _inline_image("![alt](https://example.com/img.png)", tmp_path, "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == "https://example.com/img.png"

    def test_https_url_passthrough(self, tmp_path):
        """HTTPS URLs should still be passed through as image_url type."""
        result = _inline_image("![alt](https://example.com/photo.jpg)", tmp_path, "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == "https://example.com/photo.jpg"

    def test_data_uri_base64_passthrough(self, tmp_path):
        """Data URIs with base64 encoding should still be passed through."""
        data_uri = "![img](data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==)"
        result = _inline_image(data_uri, tmp_path, "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"].startswith("data:image/png;base64,")

    def test_empty_alt_text_returns_text(self, tmp_path):
        """Empty alt text like ![](figures/14.2) from Document Intelligence should return text."""
        result = _inline_image("![](figures/14.2)", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == "![](figures/14.2)"

    def test_unparseable_markdown_image_returns_text(self, tmp_path):
        """Markdown image with title attribute that fails regex should return text, not raise."""
        result = _inline_image('![alt](url "title")', tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == '![alt](url "title")'

    def test_real_local_image_file(self, tmp_path):
        """A real local image file should still be base64-encoded as before."""
        # Create a minimal valid PNG file (1x1 pixel)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4" "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
        )
        img_path = tmp_path / "test_image.png"
        img_path.write_bytes(png_data)

        result = _inline_image(f"![test]({img_path.name})", tmp_path, "auto")
        assert result["type"] == "image_url"
        assert result["image_url"]["url"].startswith("data:")
        assert "base64" in result["image_url"]["url"]


@pytest.mark.unittest
class TestToContentStrOrListGracefulFallback:
    """Tests for _to_content_str_or_list handling of unresolvable image paths."""

    def test_text_with_unresolvable_image_ref(self, tmp_path):
        """Mixed text with unresolvable image ref should not crash."""
        result = _to_content_str_or_list("Some text ![fig](figures/1.1) more text", tmp_path, "auto")
        # Should return a list with text chunks (no crash)
        assert isinstance(result, list)
        # All chunks should be of type "text" since the image is unresolvable
        for item in result:
            assert item["type"] == "text"

    def test_plain_text_no_images(self, tmp_path):
        """Plain text with no image references should return a string."""
        result = _to_content_str_or_list("Just plain text", tmp_path, "auto")
        assert isinstance(result, str)
        assert result == "Just plain text"

    def test_text_with_http_image(self, tmp_path):
        """Text with valid HTTP image URL should return list with image_url type."""
        result = _to_content_str_or_list("Before ![alt](https://example.com/img.png) after", tmp_path, "auto")
        assert isinstance(result, list)
        image_items = [item for item in result if item["type"] == "image_url"]
        assert len(image_items) == 1
        assert image_items[0]["image_url"]["url"] == "https://example.com/img.png"

    def test_multiple_unresolvable_refs(self, tmp_path):
        """Multiple unresolvable image refs in one string should all become text."""
        result = _to_content_str_or_list("Text ![a](figures/1.1) middle ![b](figures/2.3) end", tmp_path, "auto")
        assert isinstance(result, list)
        for item in result:
            assert item["type"] == "text"

    def test_text_with_empty_alt_text_image(self, tmp_path):
        """Empty alt text image refs like ![](figures/14.2) in mixed content should not crash."""
        result = _to_content_str_or_list("Text ![](figures/14.2) more text", tmp_path, "auto")
        assert isinstance(result, list)
        for item in result:
            assert item["type"] == "text"

    def test_real_local_image_in_mixed_content(self, tmp_path):
        """Real local image file mixed with text should work as before."""
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4" "nGNgYPgPAAEDAQAIicLsAAAABJRU5ErkJggg=="
        )
        img_path = tmp_path / "real.png"
        img_path.write_bytes(png_data)

        result = _to_content_str_or_list(f"Before ![img]({img_path.name}) after", tmp_path, "auto")
        assert isinstance(result, list)
        image_items = [item for item in result if item["type"] == "image_url"]
        assert len(image_items) == 1
        assert image_items[0]["image_url"]["url"].startswith("data:")
