# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from typing import Any, Union
from uuid import uuid4
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from .._shared.utils import parse_connection_str, get_authentication_policy, get_current_utc_time
from .._generated.aio._client import AzureCommunicationEmailService
from .._version import SDK_MONIKER

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
    """
    def __init__(
            self,
            endpoint: str,
            credential: Union[AsyncTokenCredential, AzureKeyCredential],
            **kwargs
        ) -> None:
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

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
    async def send(
        self,
        email_message: JSON,
        **kwargs
    ) -> JSON:
        # cSpell:disable
        """Queues an email message to be sent to one or more recipients.

        :param email_message: The message payload for sending an email. Required.
        :type email_message: JSON
        :return: JSON object
        :rtype: JSON

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                email_message = {
                    "content": {
                        "subject": "str",  # Subject of the email message. Required.
                        "html": "str",  # Optional. Html version of the email message.
                        "plainText": "str"  # Optional. Plain text version of the email
                          message.
                    },
                    "recipients": {
                        "to": [
                            {
                                "email": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ],
                        "CC": [
                            {
                                "email": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ],
                        "bCC": [
                            {
                                "email": "str",  # Email address. Required.
                                "displayName": "str"  # Optional. Email display name.
                            }
                        ]
                    },
                    "sender": "str",  # Sender email address from a verified domain. Required.
                    "attachments": [
                        {
                            "attachmentType": "str",  # The type of attachment file.
                              Required. Known values are: "avi", "bmp", "doc", "docm", "docx", "gif",
                              "jpeg", "mp3", "one", "pdf", "png", "ppsm", "ppsx", "ppt", "pptm",
                              "pptx", "pub", "rpmsg", "rtf", "tif", "txt", "vsd", "wav", "wma", "xls",
                              "xlsb", "xlsm", and "xlsx".
                            "contentBytesBase64": "str",  # Base64 encoded contents of
                              the attachment. Required.
                            "name": "str"  # Name of the attachment. Required.
                        }
                    ],
                    "disableUserEngagementTracking": bool,  # Optional. Indicates whether user
                      engagement tracking should be disabled for this request if the resource-level
                      user engagement tracking setting was already enabled in the control plane.
                    "headers": [
                        {
                            "name": "str",  # Header name. Required.
                            "value": "str"  # Header value. Required.
                        }
                    ],
                    "importance": "normal",  # Optional. Default value is "normal". The
                      importance type for the email. Known values are: "high", "normal", and "low".
                    "replyTo": [
                        {
                            "email": "str",  # Email address. Required.
                            "displayName": "str"  # Optional. Email display name.
                        }
                    ]
                }

                # response body for status code(s): 200
                response == {
                    "messageId": "str",  # System generated id of an email message sent. Required.
                }
        """
        # cSpell:enable

        return await self._generated_client.email.send(
            repeatability_request_id=uuid4(),
            repeatability_first_sent=get_current_utc_time(),
            email_message=email_message,
            **kwargs
        )

    @distributed_trace_async
    async def get_send_status(
        self,
        message_id: str,
        **kwargs
    ) -> JSON:
        """Gets the status of a message sent previously.

        :param message_id: System generated message id (GUID) returned from a previous call to send email
        :type message_id: str
        :return: JSON object
        :rtype: JSON

        Example:
            .. code-block:: python

                # response body
                response == {
                    "messageId": "str",  # System generated id of an email message sent.
                      Required.
                    "status": "str"  # The type indicating the status of a request. Required.
                      Known values are: "queued", "outForDelivery", and "dropped".
                }
        """

        return await self._generated_client.email.get_send_status(
            message_id=message_id,
            **kwargs
        )

    async def __aenter__(self) -> "EmailClient":
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._generated_client.__aexit__(*args)

    async def close(self) -> None:
        await self._generated_client.close()
