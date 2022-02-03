# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, TypeVar
try:
    from typing import Protocol, TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

ObjectType = TypeVar("ObjectType")

class MessageType(Protocol):
    """Message Types that set and get data and content type values internally.
    """

    @classmethod
    def from_message_data(cls, data: bytes, content_type: str, **kwargs: Any) -> "MessageType":   # pylint: disable=super-init-not-called
        ...

    def __data__(self) -> bytes:
        ...

    def __content_type__(self) -> Optional[str]:
        ...

class MessageMetadataDict(TypedDict):
    """A dict with required keys:
        - `data`: bytes
        - `content_type`: str
    """

    data: bytes
    content_type: str
