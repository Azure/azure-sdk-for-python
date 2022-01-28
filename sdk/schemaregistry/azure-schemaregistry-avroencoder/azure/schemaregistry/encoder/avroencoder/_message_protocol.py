# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, TypeVar
try:
    from typing import Protocol, _TypedDict as TypedDict
except ImportError:
    from typing_extensions import Protocol, TypedDict

ObjectType = TypeVar("ObjectType")

class MessageType(Protocol):

    def __init__(self, *, data: bytes, content_type: str, **kwargs: Any) -> None:   # pylint: disable=super-init-not-called
        ...

    def __data__(self) -> bytes:
        ...

    def __content_type__(self) -> Optional[str]:
        ...

class MessageCallbackType(Protocol):

    def __call__(self, *, data: bytes, content_type: str, **kwargs: Any) -> None:
        ...

class MessageMetadataDict(TypedDict):
    data: bytes
    content_type: str
