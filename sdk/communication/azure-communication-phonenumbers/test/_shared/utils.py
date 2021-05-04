# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from .fake_token_credential import FakeTokenCredential
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.policies import HttpLoggingPolicy

def create_token_credential():
    # type: () -> FakeTokenCredential or DefaultAzureCredential
    from devtools_testutils import is_live
    if not is_live():
        return FakeTokenCredential()
    return DefaultAzureCredential()

def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "MS-CV"
        }
    )
    return http_logging_policy
