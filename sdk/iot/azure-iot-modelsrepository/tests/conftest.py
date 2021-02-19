# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest


@pytest.fixture
def arbitrary_exception():
    class ArbitraryException(Exception):
        pass

    return ArbitraryException("This exception is completely arbitrary")
