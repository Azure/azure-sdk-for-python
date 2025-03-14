# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class AccessPolicyAssignmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of an access policy assignment set."""

    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    DELETING = "Deleting"
    DELETED = "Deleted"
    CANCELED = "Canceled"
    FAILED = "Failed"


class AccessPolicyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Provisioning state of access policy."""

    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    DELETING = "Deleting"
    DELETED = "Deleted"
    CANCELED = "Canceled"
    FAILED = "Failed"


class AccessPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Built-In or Custom access policy."""

    CUSTOM = "Custom"
    BUILT_IN = "BuiltIn"


class DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Day of the week when a cache can be patched."""

    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    EVERYDAY = "Everyday"
    WEEKEND = "Weekend"


class DefaultName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """DefaultName."""

    DEFAULT = "default"


class ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of managed service identity (where both SystemAssigned and UserAssigned types are
    allowed).
    """

    NONE = "None"
    SYSTEM_ASSIGNED = "SystemAssigned"
    USER_ASSIGNED = "UserAssigned"
    SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"


class PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The current provisioning state."""

    SUCCEEDED = "Succeeded"
    CREATING = "Creating"
    DELETING = "Deleting"
    FAILED = "Failed"


class PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The private endpoint connection status."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Redis instance provisioning status."""

    CREATING = "Creating"
    DELETING = "Deleting"
    DISABLED = "Disabled"
    FAILED = "Failed"
    LINKING = "Linking"
    PROVISIONING = "Provisioning"
    RECOVERING_SCALE_FAILURE = "RecoveringScaleFailure"
    SCALING = "Scaling"
    SUCCEEDED = "Succeeded"
    UNLINKING = "Unlinking"
    UNPROVISIONING = "Unprovisioning"
    UPDATING = "Updating"
    CONFIGURING_AAD = "ConfiguringAAD"


class PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Whether or not public endpoint access is allowed for this cache.  Value is optional but if
    passed in, must be 'Enabled' or 'Disabled'. If 'Disabled', private endpoints are the exclusive
    access method. Default value is 'Enabled'.
    """

    ENABLED = "Enabled"
    DISABLED = "Disabled"


class RebootType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Which Redis node(s) to reboot. Depending on this value data loss is possible."""

    PRIMARY_NODE = "PrimaryNode"
    SECONDARY_NODE = "SecondaryNode"
    ALL_NODES = "AllNodes"


class RedisKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The Redis access key to regenerate."""

    PRIMARY = "Primary"
    SECONDARY = "Secondary"


class ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Role of the linked server."""

    PRIMARY = "Primary"
    SECONDARY = "Secondary"


class SkuFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The SKU family to use. Valid values: (C, P). (C = Basic/Standard, P = Premium)."""

    C = "C"
    P = "P"


class SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of Redis cache to deploy. Valid values: (Basic, Standard, Premium)."""

    BASIC = "Basic"
    STANDARD = "Standard"
    PREMIUM = "Premium"


class TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Optional: requires clients to use a specified TLS version (or higher) to connect (e,g, '1.0',
    '1.1', '1.2').
    """

    ONE0 = "1.0"
    ONE1 = "1.1"
    ONE2 = "1.2"


class UpdateChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Optional: Specifies the update channel for the monthly Redis updates your Redis Cache will
    receive. Caches using 'Preview' update channel get latest Redis updates at least 4 weeks ahead
    of 'Stable' channel caches. Default value is 'Stable'.
    """

    STABLE = "Stable"
    PREVIEW = "Preview"


class ZonalAllocationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Optional: Specifies how availability zones are allocated to the Redis cache. 'Automatic'
    enables zone redundancy and Azure will automatically select zones based on regional
    availability and capacity. 'UserDefined' will select availability zones passed in by you using
    the 'zones' parameter. 'NoZones' will produce a non-zonal cache. If 'zonalAllocationPolicy' is
    not passed, it will be set to 'UserDefined' when zones are passed in, otherwise, it will be set
    to 'Automatic' in regions where zones are supported and 'NoZones' in regions where zones are
    not supported.
    """

    AUTOMATIC = "Automatic"
    USER_DEFINED = "UserDefined"
    NO_ZONES = "NoZones"
