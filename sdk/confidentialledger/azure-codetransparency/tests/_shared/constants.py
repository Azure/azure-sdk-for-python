# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os

TEST_PROXY_CERT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "..", "eng", "common", "testproxy", "dotnet-devcert.crt"
    )
)

