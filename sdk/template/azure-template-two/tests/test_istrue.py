# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.template.two import istrue


def test_is_true_returns_true():
    assert istrue.is_true() is True


def test_is_true_takes_no_arguments():
    import pytest

    with pytest.raises(TypeError):
        istrue.is_true(1)


def test_extension_is_native():
    # The wheel is only worth signing if this really is a compiled module
    # rather than a pure Python fallback.
    assert istrue.__file__.endswith((".so", ".pyd", ".dylib"))
