# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    CustomService,
    Docker,
    Endpoint,
    EnvironmentVariable,
    EnvironmentVariableType,
    Image,
    ImageType,
    Protocol,
    VolumeDefinition,
    VolumeDefinitionType,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

APPLICATION_NAME = "application_name"
TARGET_PORT = "target_port"
PUBLISHED_PORT = "published_port"
DOCKER_IMAGE = "docker_image"
ENV_VARS = "environment_variables"
BIND_MOUNTS = "bind_mounts"
SOURCE = "source"
TARGET = "target"
ENV_VAR_NAME = "name"
ENV_VAR_VALUE = "value"
TARGET_PORT_MIN_VALUE = 1
TARGET_PORT_MAX_VALUE = 65535
PUBLISHED_PORT_MIN_VALUE = 1025
PUBLISHED_PORT_MAX_VALUE = 65535

class CustomApplications:

    """Custom Application Resource
    param custom_app: Custom Application flat json passed by the user
    type custom_app: dict[str any]"""

    def __init__(self, custom_app):
        self.custom_app = custom_app
        self._validate_custom_app_input()

    def _to_rest_object(self):
        endpoints = [
            Endpoint(
                name="connect",
                target=self.custom_app[TARGET_PORT],
                published=self.custom_app[PUBLISHED_PORT],
                protocol=Protocol.HTTP,
            )
        ]
        docker_image = Image(type=ImageType.DOCKER, reference=self.custom_app[DOCKER_IMAGE])
        environment_variables = {}
        bind_mounts = []
        if ENV_VARS in self.custom_app.keys():
            for env_variable in self.custom_app[ENV_VARS]:
                environment_variables[env_variable[ENV_VAR_NAME]]: EnvironmentVariable(
                    type=EnvironmentVariableType.LOCAL, value=env_variable[ENV_VAR_VALUE]
                )
        if BIND_MOUNTS in self.custom_app.keys():
            for bind_mount in self.custom_app[BIND_MOUNTS]:
                bind_mounts.append(
                    VolumeDefinition(
                        type=VolumeDefinitionType.BIND,
                        read_only=False,
                        source=bind_mount[SOURCE],
                        target=bind_mount[TARGET],
                    )
                )
        return CustomService(
            docker=Docker(privileged=True),
            environment_variables=environment_variables,
            volumes=bind_mounts,
            endpoints=endpoints,
            image=docker_image,
            name=self.custom_app[APPLICATION_NAME],
        )

    def _validate_custom_app_input(self):
        missing_property_error_message = "{} is missing in one or more of the custom applications"
        invalid_value_error_message = "Value of {} property should be between {} and {}"

        if APPLICATION_NAME not in self.custom_app.keys():
            raise ValidationException(
                message=missing_property_error_message.format(APPLICATION_NAME),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=missing_property_error_message.format(APPLICATION_NAME),
                error_category=ErrorCategory.USER_ERROR,
            )
        if not re.compile(r"^([a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?)$").search(self.custom_app[APPLICATION_NAME]):
            raise ValidationException(
                message="One or more custom applications have invalid name.",
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=missing_property_error_message.format(APPLICATION_NAME),
                error_category=ErrorCategory.USER_ERROR,
            )
        if TARGET_PORT not in self.custom_app.keys():
            raise ValidationException(
                message=missing_property_error_message.format(TARGET_PORT),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=missing_property_error_message.format(TARGET_PORT),
                error_category=ErrorCategory.USER_ERROR,
            )
        if not self.custom_app[TARGET_PORT].isdigit():
            msg = "Target port must be an integer"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        targetPort = int(self.custom_app[TARGET_PORT])
        if not (targetPort >= TARGET_PORT_MIN_VALUE and targetPort <= TARGET_PORT_MAX_VALUE):
            raise ValidationException(
                message=invalid_value_error_message.format(
                    TARGET_PORT, TARGET_PORT_MIN_VALUE, TARGET_PORT_MAX_VALUE
                ),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=invalid_value_error_message.format(
                    TARGET_PORT, TARGET_PORT_MIN_VALUE, TARGET_PORT_MAX_VALUE
                ),
                error_category=ErrorCategory.USER_ERROR,
            )
        if PUBLISHED_PORT not in self.custom_app.keys():
            raise ValidationException(
                message=missing_property_error_message.format(TARGET_PORT),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=missing_property_error_message.format(TARGET_PORT),
                error_category=ErrorCategory.USER_ERROR,
            )
        if not self.custom_app[TARGET_PORT].isdigit():
            msg = "Published port must be an integer"
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        publishedPort = int(self.custom_app[TARGET_PORT])
        if not (publishedPort >= PUBLISHED_PORT_MIN_VALUE and publishedPort <= PUBLISHED_PORT_MAX_VALUE):
            raise ValidationException(
                message=invalid_value_error_message.format(
                    PUBLISHED_PORT, PUBLISHED_PORT_MIN_VALUE, PUBLISHED_PORT_MAX_VALUE
                ),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=invalid_value_error_message.format(
                    PUBLISHED_PORT, PUBLISHED_PORT_MIN_VALUE, PUBLISHED_PORT_MAX_VALUE
                ),
                error_category=ErrorCategory.USER_ERROR,
            )
        if DOCKER_IMAGE not in self.custom_app.keys():
            raise ValidationException(
                message=missing_property_error_message.format(DOCKER_IMAGE),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=missing_property_error_message.format(DOCKER_IMAGE),
                error_category=ErrorCategory.USER_ERROR,
            )

        missing_inner_property = "One or More {} is missing property {} in one or more custom applications"
        if BIND_MOUNTS in self.custom_app.keys():
            for bindMount in self.custom_app[BIND_MOUNTS]:
                if SOURCE not in bindMount.keys():
                    raise ValidationException(
                        message=missing_inner_property.format(BIND_MOUNTS, SOURCE),
                        target=ErrorTarget.COMPUTE,
                        no_personal_data_message=missing_inner_property.format(BIND_MOUNTS, SOURCE),
                        error_category=ErrorCategory.USER_ERROR,
                    )
                if TARGET not in bindMount.keys():
                    raise ValidationException(
                        message=missing_inner_property.format(BIND_MOUNTS, SOURCE),
                        target=ErrorTarget.COMPUTE,
                        no_personal_data_message=missing_inner_property.format(BIND_MOUNTS, SOURCE),
                        error_category=ErrorCategory.USER_ERROR,
                    )

        if ENV_VARS in self.custom_app.keys():
            for envVar in self.custom_app[ENV_VARS]:
                if ENV_VAR_NAME not in envVar.keys():
                    raise ValidationException(
                        message=missing_inner_property.format(ENV_VARS, ENV_VAR_NAME),
                        target=ErrorTarget.COMPUTE,
                        no_personal_data_message=missing_inner_property.format(ENV_VARS, ENV_VAR_NAME),
                        error_category=ErrorCategory.USER_ERROR,
                    )
                if ENV_VAR_VALUE not in envVar.keys():
                    raise ValidationException(
                        message=missing_inner_property.format(ENV_VARS, ENV_VAR_VALUE),
                        target=ErrorTarget.COMPUTE,
                        no_personal_data_message=missing_inner_property.format(ENV_VARS, ENV_VAR_VALUE),
                        error_category=ErrorCategory.USER_ERROR,
                    )

        return True

    @classmethod
    def _from_rest_object(cls, obj):
        if obj is None:
            return obj
        custom_app = {}
        custom_app[APPLICATION_NAME] = obj.name
        custom_app[TARGET_PORT] = obj.endpoints[0].target
        custom_app[DOCKER_IMAGE] = obj.image.reference
        custom_app[BIND_MOUNTS] = list(
            map(lambda bindMount: {SOURCE: bindMount.source, TARGET: bindMount.target}, obj.volumes)
        )
        custom_app[ENV_VARS] = [
            {ENV_VAR_NAME: varname, ENV_VAR_VALUE: varvalue.value}
            for varname, varvalue in obj.environment_variables.items()
        ]
        return custom_app

    @staticmethod
    def _validate_custom_applications(custom_app_obj_list):
        unique_error = "Value of {} is should be unique accross all custom applications"
        all_application_names = list(map(lambda apps: apps.custom_app["application_name"], custom_app_obj_list))
        all_published_ports = list(map(lambda apps: apps.custom_app["published_port"], custom_app_obj_list))
        if len(set(all_published_ports)) != len(all_published_ports):
            raise ValidationException(
                message=unique_error.format("published_port"),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=unique_error.format("published_port"),
                error_category=ErrorCategory.USER_ERROR,
            )
        if len(set(all_application_names)) != len(all_application_names):
            raise ValidationException(
                message=unique_error.format("application_name"),
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=unique_error.format("application_name"),
                error_category=ErrorCategory.USER_ERROR,
            )
        return True