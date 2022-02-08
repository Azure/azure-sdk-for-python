# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict


class MessageMetadataDict(TypedDict):
    """A dict with required keys:
        - `data`: bytes
        - `content_type`: str
    """

    data: bytes
    content_type: str

class MessageType(Protocol):
    """Message Types that set and get data and content type values internally.
    """

    @classmethod
    def from_message_data(cls, data: bytes, content_type: str, **kwargs: Any) -> "MessageType":
        ...

    def __message_data__(self) -> MessageMetadataDict:
        ...
