from ._email_client import EmailClient

from ._generated.models import (
    EmailMessage,
    EmailCustomHeader,
    EmailContent,
    EmailImportance,
    EmailRecipients,
    EmailAddress,
    EmailAttachment,
    EmailAttachmentType,
    SendEmailResult,
    SendStatus,
    SendStatusResult
)

__all__ = [
    'EmailClient',
    'EmailMessage',
    'EmailCustomHeader',
    'EmailContent',
    'EmailImportance',
    'EmailRecipients',
    'EmailAddress',
    'EmailAttachment',
    'EmailAttachmentType',
    'SendEmailResult',
    'SendStatus',
    'SendStatusResult',
]