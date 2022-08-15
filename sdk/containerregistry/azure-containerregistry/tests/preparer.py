# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from devtools_testutils import PowerShellPreparer

acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_endpoint="https://fake_url.azurecr.io",
    containerregistry_resource_group="fake_rg",
    containerregistry_anonregistry_endpoint="https://fake_url.azurecr.io",
)
