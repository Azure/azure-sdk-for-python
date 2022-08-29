# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, IO, Union
from ._email_operations import EmailOperations as EmailOperationsGenerated
from ..models import _models, SendEmailResult

class EmailOperations(EmailOperationsGenerated):

    def __return_message_id(self, pipeline_response, _, response_headers):
        return response_headers['x-ms-request-id']

    def send(
        self,
        repeatability_request_id,  # type: str
        repeatability_first_sent,  # type: str
        email_message,  # type: Union[_models.EmailMessage, IO]
        **kwargs  # type: Any
    ):
        # type: (...) -> SendEmailResult
        """Queues an email message to be sent to one or more recipients.

        Queues an email message to be sent to one or more recipients.

        :param repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-Id and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-Id is an opaque string
         representing a client-generated, globally unique for all time, identifier for the request. It
         is recommended to use version 4 (random) UUIDs. Required.
        :type repeatability_request_id: str
        :param repeatability_first_sent: Must be sent by clients to specify that a request is
         repeatable. Repeatability-First-Sent is used to specify the date and time at which the request
         was first created in the IMF-fix date form of HTTP-date as defined in RFC7231. eg- Tue, 26 Mar
         2019 16:06:51 GMT. Required.
        :type repeatability_first_sent: str
        :param email_message: Message payload for sending an email. Required.
        :type email_message: IO
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: SendEmailResult or the result of cls(response)
        :rtype: ~azure.communication.email.models.SendEmailResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        message_id = super().send(
            repeatability_request_id,
            repeatability_first_sent,
            email_message,
            **dict(kwargs, cls=self.__return_message_id)
        )
        return SendEmailResult(message_id=message_id)
    
    send.metadata = {'url': "/emails:send"} # type: ignore

__all__ = ["EmailOperations"]  # type: List[str]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
