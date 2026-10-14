# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
import os

import pytest

from azure.ai.evaluation._evaluate._utils import (
    _IMAGE_SUBTYPE_TO_EXTENSION,
    _store_multimodal_content,
    process_message_content,
)


def _data_url(subtype: str, payload: bytes = b"not-really-an-image") -> str:
    encoded = base64.b64encode(payload).decode("ascii")
    return f"data:image/{subtype};base64,{encoded}"


def _list_all_files(root: str):
    collected = []
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            collected.append(os.path.join(dirpath, name))
    return collected


@pytest.mark.unittest
class TestMultimodalImagePathTraversal:
    def test_valid_image_is_written_inside_images_folder(self, tmp_path):
        images_folder_path = os.path.join(str(tmp_path), "images")
        os.makedirs(images_folder_path, exist_ok=True)

        content = {"type": "image_url", "image_url": {"url": _data_url("png")}}
        process_message_content(content, images_folder_path)

        # URL is rewritten to a relative images/<uuid>.png path.
        assert content["image_url"]["url"].startswith("images/")
        assert content["image_url"]["url"].endswith(".png")

        written = _list_all_files(images_folder_path)
        assert len(written) == 1
        assert os.path.dirname(os.path.realpath(written[0])) == os.path.realpath(images_folder_path)

    @pytest.mark.parametrize(
        "malicious_subtype",
        [
            "../../../../evil",
            "..%2f..%2fevil",
            "png/../../../../evil",
            "..\\..\\..\\evil",
            "svg+xml/../../evil",
        ],
    )
    def test_path_traversal_subtype_writes_nothing_outside_images(self, tmp_path, malicious_subtype):
        base_dir = str(tmp_path)
        images_folder_path = os.path.join(base_dir, "images")
        os.makedirs(images_folder_path, exist_ok=True)

        # Sentinel file one level above the images folder that must never be overwritten.
        sentinel = os.path.join(base_dir, "sentinel.txt")
        with open(sentinel, "w", encoding="utf-8") as f:
            f.write("original")

        content = {"type": "image_url", "image_url": {"url": _data_url(malicious_subtype, b"overwrite")}}
        process_message_content(content, images_folder_path)

        # Nothing was written into the images folder...
        assert _list_all_files(images_folder_path) == []
        # ...the URL was left untouched (not treated as a stored image)...
        assert content["image_url"]["url"].startswith("data:image/")
        # ...and the sentinel outside the images folder is intact.
        with open(sentinel, "r", encoding="utf-8") as f:
            assert f.read() == "original"

    def test_unknown_subtype_is_rejected(self, tmp_path):
        images_folder_path = os.path.join(str(tmp_path), "images")
        os.makedirs(images_folder_path, exist_ok=True)

        content = {"type": "image_url", "image_url": {"url": _data_url("definitely-not-an-image")}}
        process_message_content(content, images_folder_path)

        assert _list_all_files(images_folder_path) == []
        assert content["image_url"]["url"].startswith("data:image/")

    def test_allowlisted_subtypes_only_produce_safe_extensions(self):
        for subtype, ext in _IMAGE_SUBTYPE_TO_EXTENSION.items():
            assert "/" not in ext and "\\" not in ext and ".." not in ext
            assert ext.isalnum()

    def test_store_multimodal_content_handles_malicious_subtype(self, tmp_path):
        base_dir = str(tmp_path)
        sentinel = os.path.join(base_dir, "sentinel.txt")
        with open(sentinel, "w", encoding="utf-8") as f:
            f.write("original")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": _data_url("../../../../evil", b"overwrite")}},
                ],
            }
        ]
        _store_multimodal_content(messages, base_dir)

        images_folder_path = os.path.join(base_dir, "images")
        assert _list_all_files(images_folder_path) == []
        with open(sentinel, "r", encoding="utf-8") as f:
            assert f.read() == "original"
