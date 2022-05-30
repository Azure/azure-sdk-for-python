# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_01_01_preview.models import AmlComputeNodeInformation
from azure.ai.ml._schema.compute.aml_compute_node_info import AmlComputeNodeInfoSchema
from typing import Dict
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
)


class AmlComputeNodeInfo(AmlComputeNodeInformation):
    def __init__(self, **kwargs):
        """Compute node information related to a AmlCompute
        Variables are only populated by the server, and will be ignored when sending a request.
        """

        super().__init__(**kwargs)

    @property
    def current_job_name(self) -> str:
        return self.__dict__["run_id"]

    @current_job_name.setter
    def current_job_name(self, value: str) -> None:
        self.__dict__["run_id"] = value

    @classmethod
    def _from_rest_object(cls, rest_obj: AmlComputeNodeInformation) -> "AmlComputeNodeInfo":
        result = cls()
        result.__dict__.update(rest_obj.as_dict())
        return result

    def _to_dict(self) -> Dict:
        return AmlComputeNodeInfoSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
