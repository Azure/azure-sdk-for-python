# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from typing import Any, Union, IO
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._generated.aio._client import AzureCommunicationEmailService
from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

class EmailClient(object): # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Email gateway asynchronously.

    This client provides operations to send an email and monitor its status.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[AsyncTokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    :keyword api_version: Azure Communication Email API version.
        Default value is "2021-10-01-preview".
        Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
            **kwargs
        ) -> None:
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)

        authentication_policy = get_authentication_policy(endpoint, credential, decode_url=True, is_async=True)

        self._generated_client = AzureCommunicationEmailService(
            endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs
    ) -> 'EmailClient':
        """Create EmailClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of EmailClient.
        :rtype: ~azure.communication.EmailClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    @distributed_trace_async
    async def begin_send(
        self,
        message: Union[JSON, IO],
        **kwargs: Any
    ) -> AsyncLROPoller[JSON]:
        # cSpell:disable
        """Queues an email message to be sent to one or more recipients.

        Queues an email message to be sent to one or more recipients.

        :param message: Message payload for sending an email. Required.
        :type message: JSON
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of LROPoller that returns JSON object
        :rtype: ~azure.core.polling.LROPoller[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:

         Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                message = {
                    "content": {
                        "subject": "str",  # Subject of the email message. Required.
                        "html": "str",  # Optional. Html version of the email message.
                        "plainText": "str"  # Optional. Plain text version of the email
                          message.
                    },
                    "recipients": {
                        "to": [
                            {
                                "address": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ],
                        "bcc": [
                            {
                                "address": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ],
                        "cc": [
                            {
                                "address": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ]
                    },
                    "senderAddress": "str",  # Sender email address from a verified domain.
                      Required.
                    "attachments": [
                        {
                            "contentInBase64": "str",  # Base64 encoded contents of the
                              attachment. Required.
                            "contentType": "str",  # MIME type of the content being
                              attached. Required.
                            "name": "str"  # Name of the attachment. Required.
                        }
                    ],
                    "userEngagementTrackingDisabled": bool,  # Optional. Indicates whether user
                      engagement tracking should be disabled for this request if the resource-level
                      user engagement tracking setting was already enabled in the control plane.
                    "headers": {
                        "str": "str"  # Optional. Custom email headers to be passed.
                    },
                    "replyTo": [
                        {
                            "address": "str",  # Email address. Required.
                            "displayName": "str"  # Optional. Email display name.
                        }
                    ]
                }

                # response body for status code(s): 202
                response == {
                    "id": "str",  # The unique id of the operation. Use a UUID. Required.
                    "status": "str",  # Status of operation. Required. Known values are:
                      "NotStarted", "Running", "Succeeded", "Failed", and "Canceled".
                    "error": {
                        "additionalInfo": [
                            {
                                "info": {},  # Optional. The additional info.
                                "type": "str"  # Optional. The additional info type.
                            }
                        ],
                        "code": "str",  # Optional. The error code.
                        "details": [
                            ...
                        ],
                        "message": "str",  # Optional. The error message.
                        "target": "str"  # Optional. The error target.
                    }
                }
        """
        # cSpell:enable

        return await self._generated_client.email.begin_send(message=message, **kwargs)

    async def __aenter__(self) -> "EmailClient":
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._generated_client.__aexit__(*args)

    async def close(self) -> None:
        await self._generated_client.close()
