# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=unused-import
from ._patch import patch_sdk as _patch_sdk, PromptTemplate

_patch_sdk()
