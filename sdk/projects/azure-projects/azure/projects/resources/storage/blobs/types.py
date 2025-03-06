# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TypedDict, Literal, List, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter


RESOURCE = "Microsoft.Storage/storageAccounts/blobServices"
VERSION = "2024-01-01"


class ChangeFeed(TypedDict, total=False):
    enabled: Union[bool, Parameter[bool]]
    """Indicates whether change feed event logging is enabled for the Blob service."""
    retentionInDays: Union[int, Parameter[int]]
    """Indicates the duration of changeFeed retention in days. Minimum value is 1 day and maximum value is 146000 days (400 years). A null value indicates an infinite retention of the change feed."""


class BlobsCorsRule(TypedDict, total=False):
    allowedHeaders: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of headers allowed to be part of the cross-origin request."""
    allowedMethods: Required[
        Union[
            Parameter[List[str]],
            List[
                Union[
                    Literal["CONNECT", "DELETE", "GET", "HEAD", "MERGE", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"],
                    Parameter[str],
                ]
            ],
        ]
    ]
    """A list of HTTP methods that are allowed to be executed by the origin."""
    allowedOrigins: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of origin domains that will be allowed via CORS, or "*" to allow all domains."""
    exposedHeaders: Required[Union[Parameter[List[str]], List[Union[str, Parameter[str]]]]]
    """A list of response headers to expose to CORS clients."""
    maxAgeInSeconds: Required[Union[int, Parameter[int]]]
    """The number of seconds that the client/browser should cache a preflight response."""


class BlobsCorsRules(TypedDict, total=False):
    corsRules: Union[Parameter[List[BlobsCorsRule]], List[Union[BlobsCorsRule, Parameter[BlobsCorsRule]]]]
    """The List of CORS rules. You can include up to five CorsRule elements in the request."""


class DeleteRetentionPolicy(TypedDict, total=False):
    allowPermanentDelete: Union[bool, Parameter[bool]]
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    days: Union[int, Parameter[int]]
    """Indicates the number of days that the deleted item should be retained. The minimum specified value can be 1 and the maximum value can be 365."""
    enabled: Union[bool, Parameter[bool]]
    """Indicates whether DeleteRetentionPolicy is enabled."""


class LastAccessTimeTrackingPolicy(TypedDict, total=False):
    enable: Required[Union[bool, Parameter[bool]]]
    """When set to true last access time based tracking is enabled."""


class RestorePolicyProperties(TypedDict, total=False):
    days: Union[int, Parameter[int]]
    """How long this blob can be restored. It should be greater than zero and less than DeleteRetentionPolicy.days."""
    enabled: Required[Union[bool, Parameter[bool]]]
    """Blob restore is enabled if set to true."""


class BlobServiceProperties(TypedDict, total=False):
    automaticSnapshotPolicyEnabled: Union[bool, Parameter[bool]]
    """Automatic Snapshot is enabled if set to true. Deprecated in favor of isVersioningEnabled property."""
    changeFeed: Union["ChangeFeed", Parameter["ChangeFeed"]]
    """The blob service properties for change feed events."""
    containerDeleteRetentionPolicy: Union["DeleteRetentionPolicy", Parameter["DeleteRetentionPolicy"]]
    """The blob service properties for container soft delete."""
    cors: Union["BlobsCorsRules", Parameter["BlobsCorsRules"]]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    defaultServiceVersion: Union[str, Parameter[str]]
    """DefaultServiceVersion indicates the default version to use for requests to the Blob service if an incoming request’s version is not specified. Possible values include version 2008-10-27 and all more recent versions."""
    deleteRetentionPolicy: Union["DeleteRetentionPolicy", Parameter["DeleteRetentionPolicy"]]
    """The blob service properties for blob soft delete."""
    isVersioningEnabled: Union[bool, Parameter[bool]]
    """Use versioning to automatically maintain previous versions of your blobs."""
    lastAccessTimeTrackingPolicy: Union["LastAccessTimeTrackingPolicy", Parameter["LastAccessTimeTrackingPolicy"]]
    """The blob service property to configure last access time based tracking policy."""
    restorePolicy: Union["RestorePolicyProperties", Parameter["RestorePolicyProperties"]]
    """The blob service properties for blob restore policy."""


class BlobServiceResource(TypedDict, total=False):
    name: Union[Literal["default"], Parameter[str]]
    """The resource name."""
    properties: Union[BlobServiceProperties, Parameter[BlobServiceProperties]]
    """The properties of a storage account's Blob service."""
