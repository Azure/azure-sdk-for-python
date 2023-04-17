from ._version import VERSION
from ._chat_client import ChatClient
from ._chat_thread_client import ChatThreadClient
from ._generated.models import (
    SendChatMessageResult,
    ChatThreadItem,
    ChatMessageType,
    ChatError,
    ChatRetentionPolicy,
    ThreadCreationDateRetentionPolicy,
    Kind
)

from ._models import (
    ChatParticipant,
    ChatMessage,
    ChatThreadProperties,
    ChatMessageReadReceipt,
    ChatMessageContent,
    CreateChatThreadResult
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
    MicrosoftTeamsUserIdentifier,
    MicrosoftTeamsUserProperties,
    MicrosoftBotIdentifier,
    MicrosoftBotProperties,
    UnknownIdentifier
)

__all__ = [
    'ChatClient',
    'ChatRetentionPolicy',
    'ThreadCreationDateRetentionPolicy',
    'ChatThreadClient',
    'ChatMessage',
    'ChatMessageContent',
    'ChatMessageReadReceipt',
    'SendChatMessageResult',
    'ChatThreadProperties',
    'ChatThreadItem',
    'ChatParticipant',
    'ChatMessageType',
    'CreateChatThreadResult',
    'ChatError',
    'CommunicationTokenCredential',
    'CommunicationIdentifier',
    'CommunicationIdentifierKind',
    'CommunicationUserIdentifier',
    'CommunicationUserProperties',
    'MicrosoftTeamsUserIdentifier',
    'MicrosoftTeamsUserProperties',
    'identifier_from_raw_id',
    'PhoneNumberIdentifier',
    'PhoneNumberProperties',
    'MicrosoftBotIdentifier',
    'MicrosoftBotProperties',
    'UnknownIdentifier',
    'Kind'
]
__version__ = VERSION
