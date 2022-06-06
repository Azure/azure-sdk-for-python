# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from typing import Any, TYPE_CHECKING
import importlib
from .._patch import DUPLICATE_PARAMS_POLICY
from ._recovery_services_backup_passive_client import RecoveryServicesBackupPassiveClient as RecoveryServicesBackupPassiveClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

class RecoveryServicesBackupPassiveClient(RecoveryServicesBackupPassiveClientGenerated):
    __doc__ = RecoveryServicesBackupPassiveClientGenerated.__doc__
    def __init__(
        self,
        credential: "AsyncTokenCredential",
        subscription_id: str,
        base_url: str = "https://management.azure.com",
        **kwargs: Any
    ) -> None:
        per_call_policies = kwargs.pop("per_call_policies", [])
        try:
            per_call_policies.append(DUPLICATE_PARAMS_POLICY)
        except AttributeError:
            per_call_policies = [per_call_policies, DUPLICATE_PARAMS_POLICY]
        super().__init__(
            credential=credential,
            subscription_id=subscription_id,
            base_url=base_url,
            per_call_policies=per_call_policies,
            **kwargs
        )

# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
def patch_sdk():
    curr_package = importlib.import_module("azure.mgmt.recoveryservicesbackup.passivestamp.aio")
    curr_package.RecoveryServicesBackupPassiveClient = RecoveryServicesBackupPassiveClient
