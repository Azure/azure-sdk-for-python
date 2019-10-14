# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._shared.base_client import StorageAccountHostsMixin


class LeaseClient(StorageAccountHostsMixin):
    def __init__(
            self, client, lease_id=None
    ):
        self._blob_lease_client

    def acquire(self, lease_duration=-1, **kwargs):
        pass

    def renew(self, **kwargs):
        pass

    def release(self, **kwargs):
        pass

    def change(self, proposed_lease_id, **kwargs):
        pass

    def break_lease(self, lease_break_period=None, **kwargs):
        pass
