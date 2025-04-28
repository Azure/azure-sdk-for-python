# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from __future__ import annotations
from typing import Literal, Any, Union, TypedDict

from ...._bicep.expressions import Parameter


VERSION = '2024-01-01'


class BlobServicePropertiesProperties(TypedDict, total=False):
    automaticSnapshotPolicyEnabled: Union[bool, Parameter]
    """Deprecated in favor of isVersioningEnabled property."""
    changeFeed: Union[BlobServiceChangeFeed, Parameter]
    """The blob service properties for change feed events."""
    containerDeleteRetentionPolicy: Union[BlobServiceDeleteRetentionPolicy, Parameter]
    """The blob service properties for container soft delete."""
    cors: Union[BlobServiceCorsRule, Parameter]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    defaultServiceVersion: Union[str, Parameter]
    """defaultServiceVersion"""
    deleteRetentionPolicy: Union[BlobServiceDeleteRetentionPolicy, Parameter]
    """The blob service properties for blob soft delete."""
    isVersioningEnabled: Union[bool, Parameter]
    """Versioning is enabled if set to true."""
    lastAccessTimeTrackingPolicy: Union[BlobServiceLastAccessTimeTrackingPolicy, Parameter]
    """The blob service property to configure last access time based tracking policy."""
    restorePolicy: Union[BlobServiceRestorePolicyProperties, Parameter]
    """The blob service properties for blob restore policy."""


class BlobServiceChangeFeed(TypedDict, total=False):
    enabled: Union[bool, Parameter]
    """Indicates whether change feed event logging is enabled for the Blob service."""
    retentionInDays: Union[int, Parameter]
    """Indicates the duration of changeFeed retention in days. Minimum value is 1 day and maximum value is 146000 days (400 years). A null value indicates an infinite retention of the change feed."""


class BlobServiceCorsRule(TypedDict, total=False):
    allowedHeaders: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of headers allowed to be part of the cross-origin request."""
    allowedMethods: Union[Literal['CONNECT', 'OPTIONS', 'HEAD', 'MERGE', 'DELETE', 'GET', 'PATCH', 'PUT', 'TRACE', 'POST'], Parameter]
    """Required if CorsRule element is present. A list of HTTP methods that are allowed to be executed by the origin."""
    allowedOrigins: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of origin domains that will be allowed via CORS, or \"*\" to allow all domains"""
    exposedHeaders: Union[list[Union[str, Parameter]], Parameter]
    """Required if CorsRule element is present. A list of response headers to expose to CORS clients."""
    maxAgeInSeconds: Union[int, Parameter]
    """Required if CorsRule element is present. The number of seconds that the client/browser should cache a preflight response."""


class BlobServiceCorsRules(TypedDict, total=False):
    corsRules: Union[list[BlobServiceCorsRule], Parameter]
    """The List of CORS rules. You can include up to five CorsRule elements in the request."""


class BlobServiceDeleteRetentionPolicy(TypedDict, total=False):
    allowPermanentDelete: Union[bool, Parameter]
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    days: Union[int, Parameter]
    """Indicates the number of days that the deleted item should be retained. The minimum specified value can be 1 and the maximum value can be 365."""
    enabled: Union[bool, Parameter]
    """Indicates whether DeleteRetentionPolicy is enabled."""


class BlobServiceLastAccessTimeTrackingPolicy(TypedDict, total=False):
    blobType: Union[list[Union[str, Parameter]], Parameter]
    """An array of predefined supported blob types. Only blockBlob is the supported value. This field is currently read only"""
    enable: Union[bool, Parameter]
    """When set to true last access time based tracking is enabled."""
    name: Union[Literal['AccessTimeTracking'], Parameter]
    """Name of the policy. The valid value is AccessTimeTracking. This field is currently read only"""
    trackingGranularityInDays: Union[int, Parameter]
    """The field specifies blob object tracking granularity in days, typically how often the blob object should be tracked.This field is currently read only with value as 1"""


class BlobServiceResource(TypedDict, total=False):
    name: Union[Literal['default'], Parameter]
    """The resource name"""
    properties: Union[BlobServicePropertiesProperties, Parameter]
    """properties"""
    parent: Any
    """The Symbolic name of the resource that is the parent for this resource."""


class BlobServiceRestorePolicyProperties(TypedDict, total=False):
    days: Union[int, Parameter]
    """how long this blob can be restored. It should be great than zero and less than DeleteRetentionPolicy.days."""
    enabled: Union[bool, Parameter]
    """Blob restore is enabled if set to true."""

