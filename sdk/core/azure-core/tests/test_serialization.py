# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.serialization import NULL

def test_NULL_is_falsy():
    assert NULL != False
    assert (not NULL)
    assert NULL is NULL