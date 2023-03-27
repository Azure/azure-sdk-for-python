# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from .protocol._enums import (
    AttestationMechanismType,
    BulkEnrollmentGroupOperationMode,
    BulkEnrollmentOperationMode,
    DeviceRegistrationStateStatus,
    DeviceRegistrationStateSubstatus,
    EnrollmentGroupAllocationPolicy,
    EnrollmentGroupProvisioningStatus,
    IndividualEnrollmentAllocationPolicy,
    IndividualEnrollmentProvisioningStatus,
)

__all__ = [
    "AttestationMechanismType",
    "BulkEnrollmentGroupOperationMode",
    "BulkEnrollmentOperationMode",
    "DeviceRegistrationStateStatus",
    "DeviceRegistrationStateSubstatus",
    "EnrollmentGroupAllocationPolicy",
    "EnrollmentGroupProvisioningStatus",
    "IndividualEnrollmentAllocationPolicy",
    "IndividualEnrollmentProvisioningStatus",
]
