import pytest

from azure.communication.email.aio import EmailClient
from azure.communication.email import (
    EmailMessage,
    EmailContent,
    EmailRecipients,
    EmailAddress,
    EmailAttachment
)
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import email_decorator_async

class TestEmailClient(AzureRecordedTestCase):
    # TODO: Change the assert statements once x-ms-request-id change is merged in
    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_single_recipient(self):
        email_client = EmailClient(self.communication_connection_string)

        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
            )
        )

        async with email_client:
            response = await email_client.send(message)
            assert response is not None

    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_multiple_recipients(self):
        email_client = EmailClient(self.communication_connection_string)

        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[
                    EmailAddress(email=self.recipient_address, display_name="Customer Name"),
                    EmailAddress(email=self.recipient_address, display_name="Customer Name 2"),
                ]
            )
        )

        async with email_client:
            response = await email_client.send(message)
            assert response is not None

    @email_decorator_async
    @recorded_by_proxy_async
    async def test_send_email_attachment(self):
        email_client = EmailClient(self.communication_connection_string)

        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
            ),
            attachments=[
                EmailAttachment(
                    name="readme.txt",
                    attachment_type="txt",
                    content_bytes_base64="ZW1haWwgdGVzdCBhdHRhY2htZW50"
                )
            ]
        )

        async with email_client:
            response = await email_client.send(message)
            assert response is not None

    # TODO: Comment back in once the x-ms-request-id change is merged in
    # @email_decorator_async
    # @recorded_by_proxy_async
    # async def test_check_message_status(self):
    #     email_client = EmailClient(self.communication_connection_string)

    #     message = EmailMessage(
    #         sender=self.sender_address,
    #         content=EmailContent(subject="This is the subject", plain_text="This is the body"),
    #         recipients=EmailRecipients(
    #             to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
    #         )
    #     )

    #     async with email_client:
    #         response = await email_client.send(message)
    #         message_id = response.message_id
    #         if message_id is not None:
    #             message_status_response = await email_client.get_send_status(message_id)
    #             assert message_status_response.status is not None
    #         else:
    #             assert False
