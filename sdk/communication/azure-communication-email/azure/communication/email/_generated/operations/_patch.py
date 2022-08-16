# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import Any, IO, List, Union
from ._operations import EmailOperations as EmailOperationsGenerated

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

class EmailOperations(EmailOperationsGenerated):

    def __return_message_id(self, pipeline_response, _, response_headers):
        return response_headers['x-ms-request-id']

    def send(  # pylint: disable=inconsistent-return-statements
        self,
        email_message: Union[JSON, IO],
        *,
        repeatability_request_id: str,
        repeatability_first_sent: str,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Queues an email message to be sent to one or more recipients.

        Queues an email message to be sent to one or more recipients.

        :param email_message: Message payload for sending an email. Is either a model type or a IO
         type. Required.
        :type email_message: JSON or IO
        :keyword repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated, globally unique for all time, identifier for the request. It
         is recommended to use version 4 (random) UUIDs. Required.
        :paramtype repeatability_request_id: str
        :keyword repeatability_first_sent: Must be sent by clients to specify that a request is
         repeatable. Repeatability-First-Sent is used to specify the date and time at which the request
         was first created in the IMF-fix date form of HTTP-date as defined in RFC7231. eg- Tue, 26 Mar
         2019 16:06:51 GMT. Required.
        :paramtype repeatability_first_sent: str
        :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
         Default value is None.
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        message_id = super().send(
            email_message,
            repeatability_request_id=repeatability_request_id,
            repeatability_first_sent=repeatability_first_sent,
            content_type=content_type,
            cls=self.__return_message_id,
            **kwargs
        )

        return { "message_id": message_id }

    send.metadata = {'url': "/emails:send"} # type: ignore

__all__: List[str] = ["EmailOperations"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
