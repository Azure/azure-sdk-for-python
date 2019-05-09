# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class Lease(object):

    def __init__(self):
        pass

    def __enter__(self):
        raise TypeError("Please use an async context manager.")

    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.release()

    async def renew(self, if_modified_since=None, if_unmodified_since=None, if_match=None,
                    if_none_match=None, timeout=None):
        pass

    async def release(self, if_modified_since=None, if_unmodified_since=None, if_match=None,
                      if_none_match=None, timeout=None):
        pass

    async def change(self, proposed_lease_id, if_modified_since=None, if_unmodified_since=None,
                     if_match=None, if_none_match=None, timeout=None):
        pass
