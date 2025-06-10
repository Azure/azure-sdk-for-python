# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import TracebackType
from typing import Any, Dict, List, Optional, Union

from typing_extensions import Self

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ._encryption import StorageEncryptionMixin
from ._message_encoding import (
    BinaryBase64DecodePolicy,
    BinaryBase64EncodePolicy,
    TextBase64DecodePolicy,
    TextBase64EncodePolicy,
)
from ._models import (
    AccessPolicy,
    QueueMessage,
    QueueProperties,
)
from ._shared.base_client import StorageAccountHostsMixin


class QueueClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    queue_name: str
    def __init__(
        self,
        account_url: str,
        queue_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = None,
        message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None, /) -> Any: ...
    def close(self) -> None: ...
    @classmethod
    def from_queue_url(
        cls,
        queue_url: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = None,
        message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        queue_name: str,
        credential: Optional[
            Union[str, Dict[str, str], AzureNamedKeyCredential, AzureSasCredential, TokenCredential]
        ] = None,
        *,
        api_version: Optional[str] = None,
        secondary_hostname: Optional[str] = None,
        message_encode_policy: Optional[Union[BinaryBase64EncodePolicy, TextBase64EncodePolicy]] = None,
        message_decode_policy: Optional[Union[BinaryBase64DecodePolicy, TextBase64DecodePolicy]] = None,
        audience: Optional[str] = None,
        **kwargs: Any
    ) -> Self: ...
    @distributed_trace
    def create_queue(
        self, *, metadata: Optional[Dict[str, str]] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def delete_queue(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def get_queue_properties(self, *, timeout: Optional[int] = None, **kwargs: Any) -> QueueProperties: ...
    @distributed_trace
    def set_queue_metadata(
        self, metadata: Optional[Dict[str, str]] = None, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]: ...
    @distributed_trace
    def get_queue_access_policy(self, *, timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, AccessPolicy]: ...
    @distributed_trace
    def set_queue_access_policy(
        self, signed_identifiers: Dict[str, AccessPolicy], *, timeout: Optional[int] = None, **kwargs: Any
    ) -> None: ...
    @distributed_trace
    def send_message(
        self,
        content: Optional[object],
        *,
        visibility_timeout: Optional[int] = None,
        time_to_live: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> QueueMessage: ...
    @distributed_trace
    def receive_message(
        self, *, visibility_timeout: Optional[int] = None, timeout: Optional[int] = None, **kwargs: Any
    ) -> Optional[QueueMessage]: ...
    @distributed_trace
    def receive_messages(
        self,
        *,
        messages_per_page: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        max_messages: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[QueueMessage]: ...
    @distributed_trace
    def update_message(
        self,
        message: Union[str, QueueMessage],
        pop_receipt: Optional[str] = None,
        content: Optional[object] = None,
        *,
        visibility_timeout: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> QueueMessage: ...
    @distributed_trace
    def peek_messages(
        self, max_messages: Optional[int] = None, *, timeout: Optional[int] = None, **kwargs: Any
    ) -> List[QueueMessage]: ...
    @distributed_trace
    def clear_messages(self, *, timeout: Optional[int] = None, **kwargs: Any) -> None: ...
    @distributed_trace
    def delete_message(
        self,
        message: Union[str, QueueMessage],
        pop_receipt: Optional[str] = None,
        *,
        timeout: Optional[int] = None,
        **kwargs: Any
    ) -> None: ...
