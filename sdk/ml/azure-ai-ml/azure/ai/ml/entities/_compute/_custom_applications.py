# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access,redefined-builtin

from typing import Dict, List, Optional
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    CustomService,
    Docker,
    Endpoint as RestEndpoint,
    EnvironmentVariable as RestEnvironmentVariable,
    EnvironmentVariableType as RestEnvironmentVariableType,
    Image as RestImage,
    ImageType as RestImageType,
    Protocol,
    VolumeDefinition as RestVolumeDefinition,
    VolumeDefinitionType as RestVolumeDefinitionType,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.constants._compute import (
    CustomApplicationDefaults,
    DUPLICATE_APPLICATION_ERROR,
    INVALID_VALUE_ERROR,
)


class ImageSettings:
    """Specifies an image configuration for a Custom Application.

    :param reference: Image reference URL.
    :type reference: str
    """

    def __init__(self, *, reference: str):
        self.reference = reference

    def _to_rest_object(self) -> RestImage:
        return RestImage(type=RestImageType.DOCKER, reference=self.reference)

    @classmethod
    def _from_rest_object(cls, obj: RestImage) -> "ImageSettings":
        return ImageSettings(reference=obj.reference)


class EndpointsSettings:
    """Specifies an endpoint configuration for a Custom Application.

    :param target: Application port inside the container.
    :type target: int
    :param published: Port over which the application is exposed from container.
    :type published: int
    """

    def __init__(self, *, target: int, published: int):
        EndpointsSettings._validate_endpoint_settings(target=target, published=published)
        self.target = target
        self.published = published

    def _to_rest_object(self) -> RestEndpoint:
        return RestEndpoint(
            name=CustomApplicationDefaults.ENDPOINT_NAME,
            target=self.target,
            published=self.published,
            protocol=Protocol.HTTP,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestEndpoint) -> "EndpointsSettings":
        return EndpointsSettings(target=obj.target, published=obj.published)

    @classmethod
    def _validate_endpoint_settings(cls, target: int, published: int):
        ports = {
            CustomApplicationDefaults.TARGET_PORT: target,
            CustomApplicationDefaults.PUBLISHED_PORT: published,
        }
        min_value = CustomApplicationDefaults.PORT_MIN_VALUE
        max_value = CustomApplicationDefaults.PORT_MAX_VALUE

        for port_name, port in ports.items():
            message = INVALID_VALUE_ERROR.format(port_name, min_value, max_value)
            if not min_value < port < max_value:
                raise ValidationException(
                    message=message,
                    target=ErrorTarget.COMPUTE,
                    no_personal_data_message=message,
                    error_category=ErrorCategory.USER_ERROR,
                )


class VolumeSettings:
    """Specifies the Bind Mount settings for a Custom Application.

    :param source: The host path of the mount.
    :type source: str
    :param target: The path in the container for the mount.
    :type target: str
    """

    def __init__(self, *, source: str, target: str):
        self.source = source
        self.target = target

    def _to_rest_object(self) -> RestVolumeDefinition:
        return RestVolumeDefinition(
            type=RestVolumeDefinitionType.BIND,
            read_only=False,
            source=self.source,
            target=self.target,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestVolumeDefinition) -> "VolumeSettings":
        return VolumeSettings(source=obj.source, target=obj.target)


class CustomApplications:
    """Specifies the custom service application configuration.

    :param name: Name of the Custom Application.
    :type name: str
    :param image: Describes the Image Specifications.
    :type image: ImageSettings
    :param type: Type of the Custom Application.
    :type type: Optional[str]
    :param endpoints: Configuring the endpoints for the container.
    :type endpoints: List[EndpointsSettings]
    :param environment_variables: Environment Variables for the container.
    :type environment_variables: Optional[Dict[str, str]]
    :param bind_mounts: Configuration of the bind mounts for the container.
    :type bind_mounts: Optional[List[VolumeSettings]]
    """

    def __init__(
        self,
        *,
        name: str,
        image: ImageSettings,
        type: str = CustomApplicationDefaults.DOCKER,
        endpoints: List[EndpointsSettings],
        environment_variables: Optional[Dict] = None,
        bind_mounts: Optional[List[VolumeSettings]] = None,
        **kwargs
    ):
        self.name = name
        self.type = type
        self.image = image
        self.endpoints = endpoints
        self.environment_variables = environment_variables
        self.bind_mounts = bind_mounts
        self.additional_properties = kwargs

    def _to_rest_object(self):
        endpoints = None
        if self.endpoints:
            endpoints = [endpoint._to_rest_object() for endpoint in self.endpoints]

        environment_variables = None
        if self.environment_variables:
            environment_variables = {
                name: RestEnvironmentVariable(type=RestEnvironmentVariableType.LOCAL, value=value)
                for name, value in self.environment_variables.items()
            }

        volumes = None
        if self.bind_mounts:
            volumes = [volume._to_rest_object() for volume in self.bind_mounts]

        return CustomService(
            name=self.name,
            image=self.image._to_rest_object(),
            endpoints=endpoints,
            environment_variables=environment_variables,
            volumes=volumes,
            docker=Docker(privileged=True),
            additional_properties=self.additional_properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: CustomService) -> "CustomApplications":
        endpoints = []
        for endpoint in obj.endpoints:
            endpoints.append(EndpointsSettings._from_rest_object(endpoint))

        environment_variables = (
            {name: value.value for name, value in obj.environment_variables.items()}
            if obj.environment_variables
            else None
        )

        bind_mounts = []
        if obj.volumes:
            for volume in obj.volumes:
                bind_mounts.append(VolumeSettings._from_rest_object(volume))

        return CustomApplications(
            name=obj.name,
            image=ImageSettings._from_rest_object(obj.image),
            endpoints=endpoints,
            environment_variables=environment_variables,
            bind_mounts=bind_mounts,
            additional_properties=obj.additional_properties,
        )


def validate_custom_applications(custom_apps: List[CustomApplications]):
    message = DUPLICATE_APPLICATION_ERROR

    names = [app.name for app in custom_apps]
    if len(set(names)) != len(names):
        raise ValidationException(
            message=message.format("application_name"),
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=message.format("application_name"),
            error_category=ErrorCategory.USER_ERROR,
        )

    published_ports = [endpoint.published for app in custom_apps for endpoint in app.endpoints]

    if len(set(published_ports)) != len(published_ports):
        raise ValidationException(
            message=message.format("published_port"),
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=message.format("published_port"),
            error_category=ErrorCategory.USER_ERROR,
        )
