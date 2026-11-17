# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from dotenv import load_dotenv

from _sanitizers import configure_sanitizers

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def configure_test_proxy(test_proxy, patch_sleep, patch_async_sleep) -> None:
    configure_sanitizers()
