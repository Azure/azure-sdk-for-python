# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from devtools_testutils import test_proxy


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
