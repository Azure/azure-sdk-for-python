# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple, cast,
    TypeVar, TYPE_CHECKING
)

if TYPE_CHECKING:
    from datetime import datetime
    from ._generated.operations import BlobOperations, ContainerOperations
    BlobClient = TypeVar("BlobClient")
    ContainerClient = TypeVar("ContainerClient")


class BlobLeaseClientBase(object):
    def __init__(
            self, client, lease_id=None
    ):  # pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
        # type: (Union[BlobClient, ContainerClient], Optional[str]) -> None
        self.id = lease_id or str(uuid.uuid4())
        self.last_modified = None
        self.etag = None
        if hasattr(client, 'blob_name'):
            self._client = client._client.blob # pylint: disable=protected-access
        elif hasattr(client, 'container_name'):
            self._client = client._client.container # pylint: disable=protected-access
        else:
            raise TypeError("Lease must use either BlobClient or ContainerClient.")
