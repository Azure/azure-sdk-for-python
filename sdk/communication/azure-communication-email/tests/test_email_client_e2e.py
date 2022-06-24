from azure.communication.email import (
    EmailClient,
    EmailMessage,
    EmailContent,
    EmailRecipients,
    EmailAddress,
    EmailAttachment
)
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import email_decorator

class TestEmailClient(AzureRecordedTestCase):
    @email_decorator
    @recorded_by_proxy
    def test_send_email_single_recipient(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
            )
        )

        response = email_client.send(message)
        assert response.message_id is not None

    @email_decorator
    @recorded_by_proxy
    def test_send_email_multiple_recipients(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

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

        response = email_client.send(message)
        assert response.message_id is not None

    @email_decorator
    @recorded_by_proxy
    def test_send_email_attachment(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

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

        response = email_client.send(message)
        assert response.message_id is not None

    @email_decorator
    @recorded_by_proxy
    def test_check_message_status(self):
        email_client = EmailClient.from_connection_string(self.communication_connection_string)

        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
            )
        )

        response = email_client.send(message)
        message_id = response.message_id
        if message_id is not None:
            message_status_response = email_client.get_send_status(message_id)
            assert message_status_response.status is not None
        else:
            assert False
