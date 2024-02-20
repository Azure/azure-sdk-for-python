# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from ....entities._job.job_resource_configuration import BaseProperty


class TargetSelector(BaseProperty):
    """Compute target selector."""

    def __init__(
        self,
        compute_type: str,
        instance_types: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        my_resource_only: Optional[bool] = None,
        allow_spot_vm: Optional[bool] = None,
        **kwargs,
    ):
        """
        :param compute_type: Compute type that target selector could route job to.
        Example value: AmlCompute, AmlK8s.
        :type compute_type: str
        :param instance_types: List of instance_type that job could use. If no instance_types sre
        specified, all sizes are allowed. Note instance_types here only contains VM SKU.
        Example value: ["STANDARD_D2_V2", "ND24rs_v3"]. Note, this field is case sensitive.
        :type instance_types: List[str]
        :param regions: List of regions that would like to submit job to.
        If no regions are specified, all regions are allowed. Example value: ["eastus"].
        Currently it only works for ITP.
        :type regions: List[str]
        :param my_resource_only: Flag to control whether the job should be sent to the cluster
        owned by user. If False, target selector may send the job to shared cluster. Currently it
        only works for ITP.
        :type my_resource_only: bool
        :param allow_spot_vm: Flag to enable target selector service to send job to low priority VM.
        Currently it only works for ITP.
        :type allow_spot_vm: bool
        """
        super().__init__(**kwargs)
        self.compute_type = compute_type
        self.instance_types = instance_types
        self.regions = regions
        self.my_resource_only = my_resource_only
        self.allow_spot_vm = allow_spot_vm
