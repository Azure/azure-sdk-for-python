from ._version import VERSION
from ._chat_client import ChatClient
from ._chat_thread_client import ChatThreadClient
from ._generated.models import (
    SendChatMessageResult,
    ChatThreadItem,
    ChatMessageType,
    ChatError
)

from ._models import (
    ChatThreadParticipant,
    ChatMessage,
    ChatThreadProperties,
    ChatMessageReadReceipt,
    ChatMessageContent,
    CreateChatThreadResult
)

from ._shared.user_credential import CommunicationTokenCredential

__all__ = [
    'ChatClient',
    'ChatThreadClient',
    'ChatMessage',
    'ChatMessageContent',
    'ChatMessageReadReceipt',
    'SendChatMessageResult',
    'ChatThreadProperties',
    'ChatThreadItem',
    'ChatThreadParticipant',
    'ChatMessageType',
    'CreateChatThreadResult',
    'ChatError',
    'CommunicationTokenCredential'
]
__version__ = VERSION
