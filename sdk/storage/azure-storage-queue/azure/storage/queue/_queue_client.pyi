# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import TracebackType
from typing import Any

from ._encryption import StorageEncryptionMixin
from ._shared.base_client import StorageAccountHostsMixin


class QueueClient(StorageAccountHostsMixin, StorageEncryptionMixin):
    queue_name: str
    def __exit__(self, typ: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None, /) -> Any: ...
