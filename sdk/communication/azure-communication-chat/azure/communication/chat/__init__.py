from ._version import VERSION
from ._chat_client import ChatClient
from ._chat_thread_client import ChatThreadClient
from ._generated.models import ChatAttachmentType, SendChatMessageResult, ChatThreadItem, ChatMessageType, ChatError

from ._models import (
    ChatAttachment,
    ChatParticipant,
    ChatMessage,
    ChatThreadProperties,
    ChatMessageReadReceipt,
    ChatMessageContent,
    CreateChatThreadResult,
)

from ._shared.user_credential import CommunicationTokenCredential
from ._shared.models import (
    CommunicationIdentifier,
    CommunicationIdentifierKind,
    CommunicationUserIdentifier,
    CommunicationUserProperties,
    identifier_from_raw_id,
    PhoneNumberIdentifier,
    PhoneNumberProperties,
    MicrosoftTeamsAppIdentifier,
    MicrosoftTeamsAppProperties,
    MicrosoftTeamsUserIdentifier,
    MicrosoftTeamsUserProperties,
    UnknownIdentifier,
)

__all__ = [
    "ChatClient",
    "ChatThreadClient",
    "ChatMessage",
    "ChatMessageContent",
    "ChatMessageReadReceipt",
    "SendChatMessageResult",
    "ChatThreadProperties",
    "ChatThreadItem",
    "ChatParticipant",
    "ChatMessageType",
    "ChatAttachment",
    "ChatAttachmentType",
    "CreateChatThreadResult",
    "ChatError",
    "CommunicationTokenCredential",
    "CommunicationIdentifier",
    "CommunicationIdentifierKind",
    "CommunicationUserIdentifier",
    "CommunicationUserProperties",
    "MicrosoftTeamsAppIdentifier",
    "MicrosoftTeamsAppProperties",
    "MicrosoftTeamsUserIdentifier",
    "MicrosoftTeamsUserProperties",
    "identifier_from_raw_id",
    "PhoneNumberIdentifier",
    "PhoneNumberProperties",
    "UnknownIdentifier",
]
__version__ = VERSION
