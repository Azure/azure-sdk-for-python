# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from .fake_token_credential import FakeTokenCredential
from azure.identity import DefaultAzureCredential

def create_token_credential():
    # type: () -> FakeTokenCredential or DefaultAzureCredential
    from devtools_testutils import is_live
    if not is_live():
        return FakeTokenCredential()
    return DefaultAzureCredential()
