
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .._shared.policy import HMACCredentialsPolicy

class CustomHMACCredentialsPolicy(HMACCredentialsPolicy):
    def _encode_query_url(self, query_url, request):
        print("from CustomHMACCredentialsPolicy")
        return query_url
