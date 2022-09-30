# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Optional, Union
from typing_extensions import Literal

from azure.ai.ml._restclient.v2022_06_01_preview.models import JobService as RestJobService20220601Preview
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobService as RestJobService
from azure.ai.ml.entities._mixins import RestTranslatableMixin

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
        job_service_type: Optional[Literal["JupyterLab", "SSH", "TensorBoard", "VSCode"]] = None,
        status: Optional[str] = None,
        port: Optional[int] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        self.endpoint = endpoint
        self.job_service_type = job_service_type
        self.status = status
        self.port = port
        self.properties = properties

    def _to_rest_object(self) -> RestJobService:
        return RestJobService(
            endpoint=self.endpoint,
            job_service_type=self.job_service_type,
            port=self.port,
            properties=self.properties,
        )

    @classmethod
    def _to_rest_job_services(cls, services: Dict[str, "JobService"]) -> Dict[str, RestJobService]:
        if services is None:
            return None

        # pylint: disable=protected-access
        return {name: service._to_rest_object() for name, service in services.items()}

    @classmethod
    def _from_rest_object(cls, obj: Union[RestJobService, RestJobService20220601Preview]) -> "JobService":
        """RestJobService20220601Preview is supported for backward compatibility
        with v2022_06_01 version of JobService used in tests.
        In pytest the services in yaml (e.g test_job_command_job_create_skip_validation.yaml) is getting deserialized
        to v2022_06_01_preview version of JobService instead of v2022_10_01_preview.
        """
        return cls(
            endpoint=obj.endpoint,
            job_service_type=obj.job_service_type,
            status=obj.status,
            port=obj.port,
            properties=obj.properties,
        )

    @classmethod
    def _from_rest_job_services(
        cls, services: Dict[str, Union[RestJobService, RestJobService20220601Preview]]
    ) -> Dict[str, "JobService"]:
        """Resolve Dict[str, RestJobService] to Dict[str, JobService]"""
        if services is None:
            return None

        result = {}
        for name, service in services.items():
            result[name] = JobService._from_rest_object(service)
        return result
