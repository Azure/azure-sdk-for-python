# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=unused-import
try:
    import prompty  # pylint: disable=unused-import
except ImportError as exc:
    raise ImportError(
        "The 'prompty' package is required to use the 'azure.ai.projects.prompts' module. "
        "Please install it by running 'pip install prompty'."
    ) from exc

from ._patch import patch_sdk as _patch_sdk, PromptTemplate

_patch_sdk()
