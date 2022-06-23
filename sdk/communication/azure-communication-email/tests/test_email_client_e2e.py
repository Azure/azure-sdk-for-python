import os
from azure.communication.email import (
    EmailClient,
    EmailMessage,
    EmailContent,
    EmailRecipients,
    EmailAddress
)
from _shared.testcase import (
    CommunicationTestCase,
)

class EmailClientTest(CommunicationTestCase):
    def __init__(self, method_name):
        super(EmailClientTest, self).__init__(method_name)

    def setUp(self):
        super(EmailClientTest, self).setUp()

        self.sender_address = os.getenv("SENDER_ADDRESS")
        self.recipient_address = os.getenv("RECIPIENT_ADDRESS")

    def test_send_email_single(self):
        email_client = EmailClient(self.connection_str)
        
        message = EmailMessage(
            sender=self.sender_address,
            content=EmailContent(subject="This is the subject", plain_text="This is the body"),
            recipients=EmailRecipients(
                to=[EmailAddress(email=self.recipient_address, display_name="Customer Name")]
            )
        )

        response = email_client.send(message)
        print(response)
        assert response is None