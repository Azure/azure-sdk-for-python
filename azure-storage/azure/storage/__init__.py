#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from .constants import (
    __author__,
    __version__,
    X_MS_VERSION,
    BLOB_SERVICE_HOST_BASE,
    QUEUE_SERVICE_HOST_BASE,
    TABLE_SERVICE_HOST_BASE,
    DEV_BLOB_HOST,
    DEV_QUEUE_HOST,
    DEV_TABLE_HOST,
    DEV_ACCOUNT_NAME,
    DEV_ACCOUNT_KEY,
    DEFAULT_HTTP_TIMEOUT,
)

from .models import (
    EnumResultsBase,
    ContainerEnumResults,
    Container,
    Properties,
    RetentionPolicy,
    Logging,
    HourMetrics,
    MinuteMetrics,
    StorageServiceProperties,
    AccessPolicy,
    SignedIdentifier,
    SignedIdentifiers,
    BlobEnumResults,
    BlobResult,
    Blob,
    BlobProperties,
    BlobPrefix,
    BlobBlock,
    BlobBlockList,
    PageRange,
    PageList,
    QueueEnumResults,
    Queue,
    QueueMessagesList,
    QueueMessage,
    Entity,
    EntityProperty,
    Table,
    ContainerSharedAccessPermissions,
    BlobSharedAccessPermissions,
    TableSharedAccessPermissions,
    QueueSharedAccessPermissions,
)

from .blobservice import BlobService
from .queueservice import QueueService
from .tableservice import TableService
from .cloudstorageaccount import CloudStorageAccount
from .sharedaccesssignature import (
    SharedAccessSignature,
    SharedAccessPolicy,
)
from .auth import (
    _StorageSharedKeyAuthentication,
    StorageNoAuthentication,
    StorageSASAuthentication,
    StorageSharedKeyAuthentication,
    StorageTableSharedKeyAuthentication,
)
from .connection import (
    StorageConnectionParameters,
)
