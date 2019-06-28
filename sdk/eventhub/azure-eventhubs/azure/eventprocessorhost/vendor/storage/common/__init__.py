# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._constants import (
    __author__,
    __version__,
    DEFAULT_X_MS_VERSION,
)
from .cloudstorageaccount import CloudStorageAccount
from .models import (
    RetentionPolicy,
    Logging,
    Metrics,
    CorsRule,
    DeleteRetentionPolicy,
    StaticWebsite,
    ServiceProperties,
    AccessPolicy,
    ResourceTypes,
    Services,
    AccountPermissions,
    Protocol,
    ServiceStats,
    GeoReplication,
    LocationMode,
    RetryContext,
)
from .retry import (
    ExponentialRetry,
    LinearRetry,
    no_retry,
)
from .sharedaccesssignature import (
    SharedAccessSignature,
)
from .tokencredential import TokenCredential
from ._error import AzureSigningError
