from uuid import uuid4
from azure.core.tracing.decorator import distributed_trace
from ._shared.utils import parse_connection_str, get_current_utc_time
from ._shared.policy import HMACCredentialsPolicy
from ._generated._azure_communication_email_service import AzureCommunicationEmailService
from ._version import SDK_MONIKER
from ._generated.models import SendEmailResult, SendStatusResult, EmailMessage

class EmailClient(object):
    """A client to interact with the AzureCommunicationService Email gateway.

    This client provides operations to send an email and monitor its status.

    :param str conn_string:
        The connection string to connect to an Azure Communication Service resource.
        Example: "endpoint=https://contoso.eastus.communications.azure.net/;accesskey=secret";
    """
    def __init__(
            self,
            conn_str, # type: str
            **kwargs # type: Any
        ):
        # type: (...) -> None
        endpoint, access_key = parse_connection_str(conn_str)
        authentication_policy = HMACCredentialsPolicy(endpoint, access_key)

        self._generated_client = AzureCommunicationEmailService(
            endpoint,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @distributed_trace
    def send(
        self,
        email_message, # type: EmailMessage
        **kwargs # type: Any
    ): # type: (...) -> SendEmailResult
        """Queues an email message to be sent to one or more recipients.

        :param email_message: The message payload for sending an email.
        :type email_message: ~azure.communication.email.models.EmailMessage
        :return: SendEmailResult
        :rtype: ~azure.communication.email.models.SendEmailResult
        """

        return self._generated_client.email.send(
            repeatability_request_id=uuid4(),
            repeatability_first_sent=get_current_utc_time(),
            email_message=email_message,
            **kwargs
        )
    
    @distributed_trace
    def get_send_status(
        self,
        message_id, #type: str
        **kwargs # type: Any
    ): # type: (...) -> SendStatusResult
        """Gets the status of a message sent previously.

        :param message_id: System generated message id (GUID) returned from a previous call to send email
        :type message_id: str
        :return: SendStatusResult
        :rtype: ~azure.communication.email.models.SendStatusResult
        """

        return self._generated_client.email.get_send_status(
            message_id=message_id,
            **kwargs
        )
