# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class Lease(object):

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    def renew(self, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None):
        pass

    def release(self, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None):
        pass

    def change(self, proposed_lease_id, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        pass
