# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Optional
from typing_extensions import Literal

from azure.ai.ml._restclient.v2022_10_01_preview.models import AllNodes
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobService as RestJobService
from azure.ai.ml.constants._job.job import JobServicesPropertiesNames
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


class JobService(RestTranslatableMixin):
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
    :param public_keys: public key to connect to the service.
    :type public_keys: str
    """

    def __init__(
        self,
        *,
        endpoint: Optional[str] = None,
        job_service_type: Optional[Literal["JupyterLab", "SSH", "TensorBoard", "VSCode"]] = None,
        nodes: Optional[Literal["all"]] = None,
        status: Optional[str] = None,
        public_keys: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.endpoint = endpoint
        self.job_service_type = job_service_type
        self.nodes = nodes
        self.status = status
        self.public_keys = public_keys
        self.port = port
        self.properties = properties
        self._validate_nodes()

    def _to_rest_object(self) -> RestJobService:
        properties = self.properties
        if self.public_keys and properties:
            properties = {**properties, JobServicesPropertiesNames.PUBLIC_KEYS: self.public_keys}
        if self.public_keys and not properties:
            properties = {JobServicesPropertiesNames.PUBLIC_KEYS: self.public_keys}
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=self.job_service_type,
            nodes=AllNodes() if self.nodes else None,
            status=self.status,
            port=self.port,
            properties=properties,
        )

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

    @classmethod
    def _to_rest_job_services(cls, services: Dict[str, "JobService"]) -> Dict[str, RestJobService]:
        if services is None:
            return None

        # pylint: disable=protected-access
        return {name: service._to_rest_object() for name, service in services.items()}

    @classmethod
    def _from_rest_object(cls, obj: RestJobService) -> "JobService":
        publicKeys = None
        properties = None
        if obj.properties:
            publicKeys = obj.properties.get(JobServicesPropertiesNames.PUBLIC_KEYS)
            properties = {**obj.properties}
        if publicKeys:
            properties.pop(JobServicesPropertiesNames.PUBLIC_KEYS)

        return cls(
            endpoint=obj.endpoint,
            job_service_type=obj.job_service_type,
            # nodes="all" if isinstance(obj.nodes, AllNodes) else None,
            nodes="all" if obj.nodes else None,
            status=obj.status,
            publicKeys=publicKeys,
            port=obj.port,
            properties=properties,
        )

    @classmethod
    def _from_rest_job_services(cls, services: Dict[str, RestJobService]) -> Dict[str, "JobService"]:
        """Resolve Dict[str, RestJobService] to Dict[str, JobService]"""
        if services is None:
            return None

        result = {}
        for name, service in services.items():
            result[name] = JobService._from_rest_object(service)
        return result
