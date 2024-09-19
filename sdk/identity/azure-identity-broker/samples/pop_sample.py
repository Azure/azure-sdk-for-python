# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
This sample is intended to show how to get a Proof-of-Possession (PoP) token.
"""

from azure.identity.broker import PopTokenRequestOptions, InteractiveBrowserBrokerCredential

nonce = "nonce"  # needs to be a valid nonce
resource_request_url = "url"  # needs to be a valid URL
resource_request_method = "GET"  # needs to be a valid HTTP method
request_options = PopTokenRequestOptions(
    {
        "pop": {
            "nonce": nonce,
            "resource_request_url": resource_request_url,
            "resource_request_method": resource_request_method,
        }
    }
)
cred = InteractiveBrowserBrokerCredential(parent_window_handle="window_handle")
pop_token = cred.get_token_info("scope", options=request_options)
