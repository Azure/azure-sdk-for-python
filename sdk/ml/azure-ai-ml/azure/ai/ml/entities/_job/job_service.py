# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Optional, Union
from typing_extensions import Literal

from azure.ai.ml._restclient.v2022_10_01_preview.models import AllNodes
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobService as RestJobService
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._job.job import JobServiceTypeNames
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


@experimental
class JobServiceBase(RestTranslatableMixin):
    """JobService configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param error_message: Any error in the service.
    :type error_message: str
    :param job_service_type: Endpoint type.
    :type job_service_type: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["jupyter_lab", "ssh", "tensor_board", "vs_code"]] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.endpoint = endpoint
        self.job_service_type = job_service_type
        self.nodes = nodes
        self.status = status
        self.port = port
        self.properties = properties
        self._validate_nodes()
        self._validate_job_service_type_name()

    def _validate_nodes(self):
        if not self.nodes in ["all", None]:
            msg = f"nodes should be either 'all' or None, but received '{self.nodes}'."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def _validate_job_service_type_name(self):
        if self.job_service_type and not self.job_service_type in JobServiceTypeNames.ENTITY_TO_REST.keys():
            msg = (
                f"job_service_type should be one of "
                f"{JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC}, but received '{self.job_service_type}'."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    @classmethod
    def _to_rest_job_services(cls, services: Dict[str, Union["JobService", "JupyterLabJobService", "SshJobService", "TensorBoardJobService", "VsCodeJobService"]]) -> Dict[str, RestJobService]:
        if services is None:
            # TODO: return {} ?
            return None

        return {name: service._to_rest_object() for name, service in services.items()}

    @classmethod
    def _from_rest_job_services(cls, services: Dict[str, RestJobService]) -> Dict[str, Union["JobService", "JupyterLabJobService", "SshJobService", "TensorBoardJobService", "VsCodeJobService"]]:
        # """Resolve Dict[str, RestJobService] to Dict[str, JobService]"""
        if services is None:
            # TODO: return {} ?
            return None

        result = {}
        for name, service in services.items():
            if service.job_service_type == JobServiceTypeNames.RestNames.JUPYTER_LAB:
                result[name] = JupyterLabJobService._from_rest_object(service)
            if service.job_service_type == JobServiceTypeNames.RestNames.SSH:
                result[name] = SshJobService._from_rest_object(service)
            if service.job_service_type == JobServiceTypeNames.RestNames.TENSOR_BOARD:
                result[name] = TensorBoardJobService._from_rest_object(service)
            if service.job_service_type == JobServiceTypeNames.RestNames.VS_CODE:
                result[name] = VsCodeJobService._from_rest_object(service)
            else:
                result[name] = JobService._from_rest_object(service)
        return result


# **********TODO: Refactor: Create base class or util functions
@experimental
class JobService(JobServiceBase):
    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["jupyter_lab", "ssh", "tensor_board", "vs_code"]] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            job_service_type=job_service_type,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )


    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "JobService":
        return cls(
            endpoint=obj.endpoint,
            job_service_type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None)
            if obj.job_service_type
            else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            properties=obj.properties,
        )

    # TODO: Map properties
    def _to_rest_object(self) -> RestJobService:
        #print(f"############# ----------------- ######## _to_rest_object JobService ")
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.job_service_type, None)
            if self.job_service_type
            else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=self.properties,
        )

# **********TODO: Refactor: Create base class or util functions
@experimental
class SshJobService(JobServiceBase):
    def __init__(
        self,   
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["ssh"]] = "ssh",
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        ssh_public_keys: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        print(f"############# ----------------- ######## SshJobService properties {properties} ")
        super().__init__(
            endpoint=endpoint,
            job_service_type=job_service_type,
            nodes=nodes,
            status=status,
            port=port,
            properties=append_or_update_properties(properties, "sshPublicKeys", ssh_public_keys),
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "SshJobService":
        print(f"############# ----------------- ######## _from_rest_object SshJobService self.job_service_type {obj.job_service_type} ")
        return cls(
            endpoint=obj.endpoint,
            job_service_type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None)
            if obj.job_service_type
            else None,
            # obj.job_service_type,
            # nodes="all" if isinstance(obj.nodes, AllNodes) else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            ssh_public_keys=get_property(obj.properties, "sshPublicKeys"),
            properties=obj.properties,
        )

    # TODO: Map properties
    def _to_rest_object(self) -> RestJobService:
        print(f"############# ----------------- ######## _to_rest_object SshJobService self.job_service_type {self.job_service_type} ")
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.job_service_type, None)
            if self.job_service_type
            else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=self.properties,
        )


# **********TODO: Refactor: Create base class or util functions
@experimental
class TensorBoardJobService(JobServiceBase):
    def __init__(
        self,   
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["tensor_board"]] = "tensor_board",
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        log_dir: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        #print(f"############# ----------------- ######## TensorBoardJobService properties {properties} ")
        super().__init__(
            endpoint=endpoint,
            job_service_type=job_service_type,
            nodes=nodes,
            status=status,
            port=port,
            properties=append_or_update_properties(properties, "logDir", log_dir),
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "TensorBoardJobService":
        return cls(
            endpoint=obj.endpoint,
            job_service_type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None)
            if obj.job_service_type
            else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            log_dir=get_property(obj.properties, "logDir"),
            properties=obj.properties,
        )

    # TODO: Map properties
    def _to_rest_object(self) -> RestJobService:
        #print(f"############# ----------------- ######## _to_rest_object TensorBoardJobService self.properties {self.properties} ")
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.job_service_type, None)
            if self.job_service_type
            else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=self.properties,
        )


# **********TODO: Refactor: Create base class or util functions
@experimental
class JupyterLabJobService(JobServiceBase):
    def __init__(
        self,   
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["jupyter_lab"]] = "jupyter_lab",
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        #print(f"############# ----------------- ######## JupyterLabJobService properties {properties} ")
        super().__init__(
            endpoint=endpoint,
            job_service_type=job_service_type,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "JupyterLabJobService":
        return cls(
            endpoint=obj.endpoint,
            job_service_type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None)
            if obj.job_service_type
            else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            properties=obj.properties,
        )

    # TODO: Map properties
    def _to_rest_object(self) -> RestJobService:
        #print(f"############# ----------------- ######## _to_rest_object JupyterLabJobService self.properties {self.properties} ")
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.job_service_type, None)
            if self.job_service_type
            else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=self.properties,
        )



# **********TODO: Refactor: Create base class or util functions
@experimental
class VsCodeJobService(JobServiceBase):
    def __init__(
        self,   
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["vs_code"]] = "vs_code",
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        #print(f"############# ----------------- ######## VsCodeJobService properties {properties} ")
        super().__init__(
            endpoint=endpoint,
            job_service_type=job_service_type,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "VsCodeJobService":
        return cls(
            endpoint=obj.endpoint,
            job_service_type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None)
            if obj.job_service_type
            else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            properties=obj.properties,
        )

    # TODO: Map properties
    def _to_rest_object(self) -> RestJobService:
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.job_service_type, None)
            if self.job_service_type
            else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=self.properties,
        )


def append_or_update_properties(properties: Dict[str, str], key: str, value: str) -> Dict[str, str]:
    # TODO: Should we support add when value is NONE
    if value and not properties:
        properties = {key: value}

    # TODO: Should we support update when value is NONE
    if value and properties:
        properties.update({key: value})

    return properties


def get_property(properties: Dict[str, str], key: str) -> str:
    return properties.get(key, None) if properties else None