# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Dict, Optional, Union

from typing_extensions import Literal

from azure.ai.ml._restclient.v2023_04_01_preview.models import AllNodes
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    JobService as RestJobService,
)
from azure.ai.ml.constants._job.job import JobServiceTypeNames
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)

module_logger = logging.getLogger(__name__)


class JobServiceBase(RestTranslatableMixin, DictMixin):
    """Base class for job service configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param error_message: Any error in the service.
    :type error_message: str
    :param type: Endpoint type.
    :type type: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        type: Optional[  # pylint: disable=redefined-builtin
            Literal["jupyter_lab", "ssh", "tensor_board", "vs_code"]
        ] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.endpoint = endpoint
        self.type = type
        self.nodes = nodes
        self.status = status
        self.port = port
        self.properties = properties
        self._validate_nodes()
        self._validate_type_name()

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

    def _validate_type_name(self):
        if self.type and not self.type in JobServiceTypeNames.ENTITY_TO_REST.keys():
            msg = (
                f"type should be one of " f"{JobServiceTypeNames.NAMES_ALLOWED_FOR_PUBLIC}, but received '{self.type}'."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

    def _to_rest_job_service(self, updated_properties: Dict[str, str] = None) -> RestJobService:
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=JobServiceTypeNames.ENTITY_TO_REST.get(self.type, None) if self.type else None,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=updated_properties if updated_properties else self.properties,
        )

    @classmethod
    def _to_rest_job_services(
        cls,
        services: Dict[
            str,
            Union["JobService", "JupyterLabJobService", "SshJobService", "TensorBoardJobService", "VsCodeJobService"],
        ],
    ) -> Dict[str, RestJobService]:
        if services is None:
            return None

        return {name: service._to_rest_object() for name, service in services.items()}

    @classmethod
    def _from_rest_job_service_object(cls, obj: RestJobService):
        return cls(
            endpoint=obj.endpoint,
            type=JobServiceTypeNames.REST_TO_ENTITY.get(obj.job_service_type, None) if obj.job_service_type else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            port=obj.port,
            # ssh_public_keys=get_property(obj.properties, "sshPublicKeys"),
            properties=obj.properties,
        )

    @classmethod
    def _from_rest_job_services(
        cls, services: Dict[str, RestJobService]
    ) -> Dict[
        str, Union["JobService", "JupyterLabJobService", "SshJobService", "TensorBoardJobService", "VsCodeJobService"]
    ]:
        # """Resolve Dict[str, RestJobService] to Dict[str, Specific JobService]"""
        if services is None:
            return None

        result = {}
        for name, service in services.items():
            if service.job_service_type == JobServiceTypeNames.RestNames.JUPYTER_LAB:
                result[name] = JupyterLabJobService._from_rest_object(service)
            elif service.job_service_type == JobServiceTypeNames.RestNames.SSH:
                result[name] = SshJobService._from_rest_object(service)
            elif service.job_service_type == JobServiceTypeNames.RestNames.TENSOR_BOARD:
                result[name] = TensorBoardJobService._from_rest_object(service)
            elif service.job_service_type == JobServiceTypeNames.RestNames.VS_CODE:
                result[name] = VsCodeJobService._from_rest_object(service)
            else:
                result[name] = JobService._from_rest_object(service)
        return result


class JobService(JobServiceBase):
    """Basic job service configuration for backward compatibility. Use JupyterLabJobService, SshJobService,
    TensorBoardJobService or VsCodeJobService specific to your job type instead of JobService.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param type: Endpoint type.
        Accepts "jupyter_lab", "ssh", "tensor_board", "vs_code"
    :type type: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "JobService":
        return cls._from_rest_job_service_object(obj)

    def _to_rest_object(self) -> RestJobService:
        return self._to_rest_job_service()


class SshJobService(JobServiceBase):
    """SSH job service configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param ssh_public_keys: SSH Public Key to access job container via SSH.
    :type ssh_public_keys: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :ivar type: Specifies the type of job service. Set automatically to "ssh" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        ssh_public_keys: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )
        self.type = JobServiceTypeNames.EntityNames.SSH
        self.ssh_public_keys = ssh_public_keys

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "SshJobService":
        ssh_job_service = cls._from_rest_job_service_object(obj)
        ssh_job_service.ssh_public_keys = get_property(obj.properties, "sshPublicKeys")
        return ssh_job_service

    def _to_rest_object(self) -> RestJobService:
        updated_properties = append_or_update_properties(self.properties, "sshPublicKeys", self.ssh_public_keys)
        return self._to_rest_job_service(updated_properties)


class TensorBoardJobService(JobServiceBase):
    """TensorBoard job service configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param log_dir: Log directory path.
    :type log_dir: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :ivar type: Specifies the type of job service. Set automatically to "tensor_board" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        log_dir: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )
        self.type = JobServiceTypeNames.EntityNames.TENSOR_BOARD
        self.log_dir = log_dir

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "TensorBoardJobService":
        tensorboard_job_Service = cls._from_rest_job_service_object(obj)
        tensorboard_job_Service.log_dir = get_property(obj.properties, "logDir")
        return tensorboard_job_Service

    def _to_rest_object(self) -> RestJobService:
        updated_properties = append_or_update_properties(self.properties, "logDir", self.log_dir)
        return self._to_rest_job_service(updated_properties)


class JupyterLabJobService(JobServiceBase):
    """JupyterLab job service configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :ivar type: Specifies the type of job service. Set automatically to "jupyter_lab" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )
        self.type = JobServiceTypeNames.EntityNames.JUPYTER_LAB

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "JupyterLabJobService":
        return cls._from_rest_job_service_object(obj)

    def _to_rest_object(self) -> RestJobService:
        return self._to_rest_job_service()


class VsCodeJobService(JobServiceBase):
    """VS Code job service configuration.

    :param endpoint: Url for endpoint.
    :type endpoint: str
    :param port: Port for endpoint.
    :type nodes: str
    :param nodes: Indicates whether the service has to run in all nodes.
    :type port: int
    :param properties: Additional properties to set on the endpoint.
    :type properties: dict[str, str]
    :param status: Status of endpoint.
    :type status: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :ivar type: Specifies the type of job service. Set automatically to "vs_code" for this class.
    :vartype type: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            nodes=nodes,
            status=status,
            port=port,
            properties=properties,
            **kwargs,
        )
        self.type = JobServiceTypeNames.EntityNames.VS_CODE

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "VsCodeJobService":
        return cls._from_rest_job_service_object(obj)

    def _to_rest_object(self) -> RestJobService:
        return self._to_rest_job_service()


def append_or_update_properties(properties: Dict[str, str], key: str, value: str) -> Dict[str, str]:
    if value and not properties:
        properties = {key: value}

    if value and properties:
        properties.update({key: value})
    return properties


def get_property(properties: Dict[str, str], key: str) -> str:
    return properties.get(key, None) if properties else None
