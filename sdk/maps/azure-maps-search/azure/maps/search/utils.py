# # ------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for
# # license information.
# # -------------------------------------------------------------------------

# import os
# from typing import Any

# from azure.core.pipeline._base import SansIOHTTPPolicy

# from azure.identity import DefaultAzureCredential
# from azure.core.pipeline.policies import HeadersPolicy
# from azure.core.credentials import TokenCredential, AzureKeyCredential


# SUBSCRIPTION_KEY_HEADER_NAME="subscription-key"
# CLIENT_ID_HEADER_NAME="x-ms-client-id"

# class AzureKeyInQueryCredentialPolicy(SansIOHTTPPolicy):
#     """Adds a key in query for the provided credential.

#     :param credential: The credential used to authenticate requests.
#     :type credential: ~azure.core.credentials.AzureKeyCredential
#     :param str name: The name of the key in query used for the credential.
#     :raises: ValueError or TypeError
#     """

#     def __init__(self, credential, name, **kwargs):  # pylint: disable=unused-argument
#         # type: (AzureKeyCredential, str, **Any) -> None
#         super(AzureKeyInQueryCredentialPolicy, self).__init__()
#         self._credential = credential
#         self._name = name



# def get_authentication_policy(credential):
#     authentication_policy=None
#     if credential is None:
#         raise ValueError("Parameter 'credential' must not be None.")
#     if isinstance(credential, AzureKeyCredential):
#         authentication_policy = AzureKeyInQueryCredentialPolicy(
#             AzureKeyCredential(os.environ.get("SUBSCRIPTION_KEY")), SUBSCRIPTION_KEY_HEADER_NAME
#         )
#     elif credential is not None and not hasattr(credential, "get_token"):
#         raise TypeError(
#             f'Unsupported credential: {type(credential)}. Use an instance of AzureKeyCredential '
#             'or a token credential from azure.identity'
#         )
#     return authentication_policy


# def get_headers_policy(credential):
#     headers_policy=None
#     if credential is None:
#         headers_policy=HeadersPolicy({CLIENT_ID_HEADER_NAME: os.environ.get("CLIENT_ID", None)})
#     return headers_policy
