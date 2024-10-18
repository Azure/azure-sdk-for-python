# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from pathlib import Path

from .constants import (
    CONFIGURATION_NAME_FACE_API_ENDPOINT,
    CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY,
)


def get_face_endpoint(**kwargs):
    return kwargs.pop(CONFIGURATION_NAME_FACE_API_ENDPOINT)


def get_account_key(**kwargs):
    return kwargs.pop(CONFIGURATION_NAME_FACE_API_ACCOUNT_KEY)


def get_image_path(image_file_name: str):
    from .constants import TestImages

    return Path(__file__).resolve().parent / (TestImages.IMAGE_PARENT_FOLDER + "/" + image_file_name)


def read_file_content(file_path: Path):
    with open(file_path, "rb") as fd:
        file_content = fd.read()

    return file_content
