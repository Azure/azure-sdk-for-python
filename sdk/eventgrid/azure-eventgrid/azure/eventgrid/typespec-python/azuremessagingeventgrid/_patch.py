# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import AzureKeyCredential

from ._client import AzureMessagingEventGridClient as ServiceClientGenerated


class EventGridSharedAccessKeyPolicy(SansIOHTTPPolicy):
    def __init__(
        self,
        credential: "AzureKeyCredential",
        **kwargs # pylint: disable=unused-argument
    ) -> None:
        super(EventGridSharedAccessKeyPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request):
        request.http_request.headers["Authorization"] = "SharedAccessKey " + self._credential.key

class AzureMessagingEventGridClient(ServiceClientGenerated):

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs):
        if isinstance(credential, AzureKeyCredential):
            # if it's our credential, we default to our authentication policy.
            # Otherwise, we use the default
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = EventGridSharedAccessKeyPolicy(credential)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            **kwargs
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = ["AzureMessagingEventGridClient"]  # Add all objects you want publicly available to users at this package level