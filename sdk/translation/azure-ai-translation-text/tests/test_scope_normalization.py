# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.ai.translation.text._patch import normalize_scope


@pytest.mark.parametrize(
    "audience, expected",
    [
        ("https://cognitiveservices.azure.com", "https://cognitiveservices.azure.com/.default"),
        ("https://cognitiveservices.azure.com/", "https://cognitiveservices.azure.com/.default"),
        ("https://cognitiveservices.azure.com/.default", "https://cognitiveservices.azure.com/.default"),
        ("api://myapp-live", "api://myapp-live/.default"),
        (None, "https://cognitiveservices.azure.com/.default"),
    ],
)
def test_normalize_scope(audience, expected):
    assert normalize_scope(audience) == expected
