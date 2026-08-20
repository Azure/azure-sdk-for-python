# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from azure.mgmt.platformvalidation.models import (
    CertificationPackageReference,
    DiskImage,
    ExecutionPlanConfiguration,
    StorageProfile,
    ValidationStep,
    ValidationExecutionPlanProperties,
)

plan = ExecutionPlanConfiguration(
    name="contoso-linux-cert",
    certification_package_reference=CertificationPackageReference(
        os_type="Linux",
        vm_generation_type="V1",
        architecture_type="X64",
        recommended_vm_sizes=["Standard_D4s_v3"],
        storage_profile=StorageProfile(
            os_disk_image=DiskImage(source_vhd_uri="https://contoso.example/img.vhd")
        ),
    ),
    steps=[
        ValidationStep.test(
            name="os-disk-size",
            test_ref="/providers/Microsoft.Validate/validationTests/os-disk-size/versions/1.0.0",
        )
    ],
)

properties = ValidationExecutionPlanProperties(plan_configuration_json=plan.to_json())
