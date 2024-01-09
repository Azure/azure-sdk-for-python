# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Union
from uuid import uuid4
from azure.core.tracing.decorator import distributed_trace
from azure.communication.sms._generated.models import (
    MmsSendMessageRequest,
    MmsRecipient,
    MmsSendOptions,
    MmsAttachment
)
from azure.communication.sms._models import MmsSendResult
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._generated._azure_communication_sms_service import AzureCommunicationSMSService
from ._shared.auth_policy_utils import get_authentication_policy
from ._shared.utils import parse_connection_str, get_current_utc_time
from ._version import SDK_MONIKER


class MmsClient(object): # pylint: disable=client-accepts-api-version-keyword
    """A client to interact with the AzureCommunicationService Mms gateway.

    This client provides operations to send a MMS via a phone number.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential we use to authenticate against the service.
    """
    def __init__(
            self, endpoint,  # type: str
            credential,  # type: Union[TokenCredential, AzureKeyCredential]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.") # pylint: disable=raise-missing-from

        if not credential:
            raise ValueError(
                "invalid credential from connection string.")

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._sms_service_client = AzureCommunicationSMSService(
            self._endpoint,
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> MmsClient
        """Create MmsClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of MmsClient.
        :rtype: ~azure.communication.MmsClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace
    def send(self, from_,  # type: str
             to,  # type: Union[str, List[str]]
             message,  # type: str
             attachments,  # type: List[MmsAttachment]
             **kwargs  # type: Any
        ): # type: (...) -> [MmsSendResult]
        """Sends MMSs to phone numbers.

        :param str from_: The sender of the MMS.
        :param to: The single recipient or the list of recipients of the MMS.
        :type to: Union[str, List[str]]
        :param str message: The message in the MMS
        :param attachments: The message attachments
        :type attachments: List[MmsAttachment]
        :keyword bool enable_delivery_report: Enable this flag to receive a delivery report for this
         message on the Azure Resource EventGrid.
        :keyword str tag: Use this field to provide metadata that will then be sent back in the corresponding
         Delivery Report.
        :return: A list of MmsSendResult.
        :rtype: [~azure.communication.sms.models.MmsSendResult]
        """

        if isinstance(to, str):
            to = [to]

        enable_delivery_report = kwargs.pop('enable_delivery_report', False)
        tag = kwargs.pop('tag', None)

        send_options = MmsSendOptions(
            enable_delivery_report=enable_delivery_report,
            tag=tag
        )

        request = MmsSendMessageRequest(
            from_property=from_,
            recipients=[
                MmsRecipient(
                    to=p,
                    repeatability_request_id=str(uuid4()),
                    repeatability_first_sent=get_current_utc_time()
                ) for p in to
            ],
            message=message,
            attachments=attachments,
            send_options=send_options,
            **kwargs)

        return self._sms_service_client.mms.send(
            request,
            cls=lambda pr, r, e: [
                MmsSendResult(
                    to=item.to,
                    message_id=item.message_id,
                    http_status_code=item.http_status_code,
                    successful=item.successful,
                    error_message=item.error_message
                ) for item in r.value
            ],
            **kwargs)
