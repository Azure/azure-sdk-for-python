# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import base64
import json
import logging
import os
from pathlib import Path

import pytest

from azure.ai.evaluation._legacy.prompty import _utils as prompty_utils
from azure.ai.evaluation._legacy.prompty._exceptions import InvalidInputError
from azure.ai.evaluation._legacy.prompty._utils import _inline_image, _to_content_str_or_list, build_messages


def _symlink_or_skip(link_path, target_path, *, target_is_directory=False):
    try:
        link_path.symlink_to(target_path, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError):
        pytest.skip("Creating symlinks is not supported in this test environment.")


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

    def test_filename_exceeds_os_limit_returns_text(self, tmp_path):
        """A filename exceeding the OS name limit (255 chars on Linux) should return text, not raise."""
        long_name = "a" * 300 + ".png"
        result = _inline_image(f"![alt]({long_name})", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == f"![alt]({long_name})"

    def test_path_with_null_byte_returns_text(self, tmp_path):
        """A path containing a null byte should return text, not raise."""
        result = _inline_image("![alt](invalid\x00path.png)", tmp_path, "auto")
        assert result["type"] == "text"
        assert result["text"] == "![alt](invalid\x00path.png)"

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

    def test_parent_traversal_returns_text(self, tmp_path):
        """A local image reference cannot escape the Prompty directory."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        (tmp_path / "outside.png").write_bytes(b"outside")
        image = "![test](../outside.png)"

        result = _inline_image(image, working_dir, "auto")

        assert result == {"type": "text", "text": image}

    def test_mixed_separator_parent_traversal_returns_text(self, tmp_path):
        """Windows separators cannot bypass containment on other platforms."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        (tmp_path / "outside.png").write_bytes(b"outside")
        image = r"![test](..\outside.png)"

        result = _inline_image(image, working_dir, "auto")

        assert result == {"type": "text", "text": image}

    def test_absolute_path_returns_text(self, tmp_path):
        """Absolute paths are not valid local Prompty image references."""
        image_path = tmp_path / "inside.png"
        image_path.write_bytes(b"inside")
        image = f"![test]({image_path.as_posix()})"

        result = _inline_image(image, tmp_path, "auto")

        assert result == {"type": "text", "text": image}

    def test_windows_absolute_path_returns_text(self, tmp_path):
        """Windows drive paths are rejected on every operating system."""
        image = r"![test](C:\outside.png)"

        result = _inline_image(image, tmp_path, "auto")

        assert result == {"type": "text", "text": image}

    @pytest.mark.parametrize(
        "local_path",
        [r"C:outside.png", r"\\server\share\outside.png", r"\\?\C:\outside.png", "/outside.png"],
    )
    def test_other_absolute_path_forms_return_text(self, tmp_path, local_path):
        image = f"![test]({local_path})"

        assert _inline_image(image, tmp_path, "auto") == {"type": "text", "text": image}

    @pytest.mark.parametrize("local_path", ["images/inside.png", r"images\inside.png", "images/../inside.png"])
    def test_nested_relative_paths_remain_supported(self, tmp_path, local_path):
        (tmp_path / "images").mkdir()
        (tmp_path / "images" / "inside.png").write_bytes(b"inside")
        (tmp_path / "inside.png").write_bytes(b"inside")

        result = _inline_image(f"![test]({local_path})", tmp_path, "auto")

        assert result["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(b'inside').decode('utf-8')}"

    def test_missing_image_does_not_log_absolute_working_directory(self, tmp_path, caplog):
        with caplog.at_level(logging.DEBUG, logger=prompty_utils.__name__):
            result = _inline_image("![test](missing.png)", tmp_path, "auto")

        assert result == {"type": "text", "text": "![test](missing.png)"}
        assert "missing.png" in caplog.text
        assert str(tmp_path) not in caplog.text
        assert tmp_path.as_posix() not in caplog.text

    def test_directory_reference_returns_text(self, tmp_path):
        (tmp_path / "directory.png").mkdir()
        image = "![test](directory.png)"

        assert _inline_image(image, tmp_path, "auto") == {"type": "text", "text": image}

    def test_symlink_escape_returns_text(self, tmp_path):
        """A symlink inside the Prompty directory cannot target an outside file."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        outside_path = tmp_path / "outside.png"
        outside_path.write_bytes(b"outside")
        symlink_path = working_dir / "linked.png"
        _symlink_or_skip(symlink_path, outside_path)

        result = _inline_image("![test](linked.png)", working_dir, "auto")

        assert result == {"type": "text", "text": "![test](linked.png)"}

    def test_contained_symlink_remains_supported(self, tmp_path):
        (tmp_path / "inside.png").write_bytes(b"inside")
        _symlink_or_skip(tmp_path / "linked.png", tmp_path / "inside.png")

        result = _inline_image("![test](linked.png)", tmp_path, "auto")

        assert result["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(b'inside').decode('utf-8')}"

    @pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor traversal test")
    @pytest.mark.parametrize("swap_target", ["file", "directory", "root_ancestor"])
    def test_posix_path_swap_before_open_is_rejected(self, tmp_path, monkeypatch, swap_target):
        parent_dir = tmp_path / "parent"
        working_dir = parent_dir / "prompty"
        image_dir = working_dir / "images"
        image_dir.mkdir(parents=True)
        inside_path = image_dir / "inside.png"
        inside_path.write_bytes(b"inside")
        outside_dir = tmp_path / "outside"
        outside_image_dir = outside_dir / "prompty" / "images"
        outside_image_dir.mkdir(parents=True)
        outside_path = outside_image_dir / "inside.png"
        outside_path.write_bytes(b"outside")
        original_open = os.open
        swapped = False

        def swap_then_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if not swapped and (
                (swap_target == "file" and path == "inside.png")
                or (swap_target == "directory" and path == "images")
                or (swap_target == "root_ancestor" and path in ("parent", working_dir))
            ):
                if swap_target == "file":
                    inside_path.unlink()
                    _symlink_or_skip(inside_path, outside_path)
                elif swap_target == "directory":
                    image_dir.rename(working_dir / "original-images")
                    _symlink_or_skip(image_dir, outside_image_dir, target_is_directory=True)
                else:
                    parent_dir.rename(tmp_path / "original-parent")
                    _symlink_or_skip(parent_dir, outside_dir, target_is_directory=True)
                swapped = True
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", swap_then_open)
        monkeypatch.setattr(os, "supports_dir_fd", os.supports_dir_fd | {swap_then_open})

        image = "![test](images/inside.png)"
        assert _inline_image(image, working_dir, "auto") == {"type": "text", "text": image}
        assert swapped

    @pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor traversal test")
    def test_posix_directory_swap_after_open_uses_opened_directory(self, tmp_path, monkeypatch):
        image_dir = tmp_path / "images"
        image_dir.mkdir()
        (image_dir / "inside.png").write_bytes(b"inside")
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()
        (outside_dir / "inside.png").write_bytes(b"outside")
        original_open = os.open
        swapped = False

        def open_then_swap(path, flags, *args, **kwargs):
            nonlocal swapped
            descriptor = original_open(path, flags, *args, **kwargs)
            if path == "images" and not swapped:
                image_dir.rename(tmp_path / "original-images")
                _symlink_or_skip(image_dir, outside_dir, target_is_directory=True)
                swapped = True
            return descriptor

        monkeypatch.setattr(os, "open", open_then_swap)
        monkeypatch.setattr(os, "supports_dir_fd", os.supports_dir_fd | {open_then_swap})

        result = _inline_image("![test](images/inside.png)", tmp_path, "auto")

        assert swapped
        assert result["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(b'inside').decode('utf-8')}"

    @pytest.mark.skipif(os.name == "nt", reason="POSIX FIFO handling test")
    def test_posix_fifo_is_rejected_without_blocking(self, tmp_path, monkeypatch):
        os.mkfifo(tmp_path / "pipe.png")
        original_open = os.open

        def require_nonblocking(path, flags, *args, **kwargs):
            if path == "pipe.png":
                assert flags & os.O_NONBLOCK, "Special files must not block before the file-type check."
            return original_open(path, flags, *args, **kwargs)

        monkeypatch.setattr(os, "open", require_nonblocking)
        monkeypatch.setattr(os, "supports_dir_fd", os.supports_dir_fd | {require_nonblocking})

        image = "![test](pipe.png)"
        assert _inline_image(image, tmp_path, "auto") == {"type": "text", "text": image}

    @pytest.mark.skipif(os.name == "nt", reason="POSIX descriptor traversal test")
    def test_posix_path_swap_after_open_uses_opened_file(self, tmp_path, monkeypatch):
        """A POSIX pathname swap after open cannot redirect the already-open descriptor."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        inside_path = working_dir / "inside.png"
        inside_path.write_bytes(b"inside")
        outside_path = tmp_path / "outside.png"
        outside_path.write_bytes(b"outside")
        swapped = False

        def swap_to_outside():
            nonlocal swapped
            inside_path.unlink()
            _symlink_or_skip(inside_path, outside_path)
            swapped = True

        original_fdopen = os.fdopen

        def swap_then_fdopen(file_descriptor, *args, **kwargs):
            if not swapped:
                swap_to_outside()
            return original_fdopen(file_descriptor, *args, **kwargs)

        monkeypatch.setattr(os, "fdopen", swap_then_fdopen)

        result = _inline_image("![test](inside.png)", working_dir, "auto")

        assert swapped is True
        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(b'inside').decode('utf-8')}"

    @pytest.mark.skipif(os.name != "nt", reason="Windows opened-handle validation test")
    def test_windows_opened_handle_outside_root_is_rejected(self, tmp_path, monkeypatch):
        """The final path derived from a Windows file handle must remain inside the Prompty directory."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        inside_path = working_dir / "inside.png"
        inside_path.write_bytes(b"inside")
        outside_path = tmp_path / "outside.png"
        outside_path.write_bytes(b"outside")
        original_open = Path.open
        opened_handles = []

        def open_outside_path(path, *args, **kwargs):
            if path == inside_path:
                handle = original_open(outside_path, *args, **kwargs)
                opened_handles.append(handle)
                return handle
            return original_open(path, *args, **kwargs)

        monkeypatch.setattr(Path, "open", open_outside_path)

        result = _inline_image("![test](inside.png)", working_dir, "auto")

        assert len(opened_handles) == 1
        assert opened_handles[0].closed
        assert result == {"type": "text", "text": "![test](inside.png)"}

    @pytest.mark.skipif(os.name != "nt", reason="Windows opened-handle validation test")
    def test_windows_handle_validation_failure_does_not_inline_file(self, tmp_path, monkeypatch):
        (tmp_path / "inside.png").write_bytes(b"inside")

        def fail_validation(_file_handle):
            raise OSError("Cannot validate the opened file.")

        monkeypatch.setattr(prompty_utils, "_get_windows_final_path", fail_validation)
        image = "![test](inside.png)"

        assert _inline_image(image, tmp_path, "auto") == {"type": "text", "text": image}

    def test_data_path_parent_traversal_raises_invalid_input(self, tmp_path):
        """The explicit data path form rejects paths outside the Prompty directory."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        (tmp_path / "outside.png").write_bytes(b"outside")

        with pytest.raises(InvalidInputError, match="within the Prompty directory"):
            _inline_image("![test](data:image/png;path:../outside.png)", working_dir, "auto")

    def test_data_path_local_image_file(self, tmp_path):
        """The explicit data path form still inlines a file within the Prompty directory."""
        (tmp_path / "inside.png").write_bytes(b"inside")

        result = _inline_image("![test](data:image/png;path:inside.png)", tmp_path, "auto")

        assert result["type"] == "image_url"
        assert result["image_url"]["url"] == f"data:image/png;base64,{base64.b64encode(b'inside').decode('utf-8')}"

    def test_data_path_absolute_reference_raises_invalid_input(self, tmp_path):
        outside_path = tmp_path / "outside.png"
        outside_path.write_bytes(b"outside")

        with pytest.raises(InvalidInputError, match="Absolute local image paths"):
            _inline_image(f"![test](data:image/png;path:{outside_path.as_posix()})", tmp_path, "auto")

    def test_build_messages_does_not_inline_outside_files_from_rendered_input(self, tmp_path):
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        outside_path = tmp_path / "outside.txt"
        outside_contents = b"outside test file contents"
        outside_path.write_bytes(outside_contents)
        response = f"Before ![first]({outside_path.as_posix()}) between ![second](../outside.txt) after"

        messages = build_messages(
            prompt="system:\nAssess the response.\nuser:\n{{ response }}",
            working_dir=working_dir,
            response=response,
        )

        assert len(messages) == 2
        assert all(item["type"] == "text" for item in messages[1]["content"])
        assert base64.b64encode(outside_contents).decode("utf-8") not in json.dumps(messages)


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

    def test_text_with_existing_parent_image_ref(self, tmp_path):
        """Mixed content cannot inline an existing image outside the Prompty directory."""
        working_dir = tmp_path / "prompty"
        working_dir.mkdir()
        (tmp_path / "outside.png").write_bytes(b"outside")

        result = _to_content_str_or_list("Before ![img](../outside.png) after", working_dir, "auto")

        assert isinstance(result, list)
        assert all(item["type"] == "text" for item in result)

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

    def test_text_with_filename_exceeding_os_limit(self, tmp_path):
        """A filename exceeding OS limits in mixed content should become text, not crash."""
        long_name = "b" * 300 + ".png"
        result = _to_content_str_or_list(f"Text ![img]({long_name}) end", tmp_path, "auto")
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
