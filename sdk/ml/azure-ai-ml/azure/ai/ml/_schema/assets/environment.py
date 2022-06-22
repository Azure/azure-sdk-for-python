# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._restclient.v2022_05_01.models import (
    OperatingSystemType,
    Route,
    InferenceContainerProperties,
)
from azure.ai.ml._schema import NestedField, PatchedSchemaMeta, UnionField
from .asset import AssetSchema, AnonymousAssetSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType
from marshmallow import ValidationError, fields, post_load, pre_dump, pre_load

from ..core.fields import ArmStr, StringTransformedEnum, VersionField, RegistryStr

from azure.ai.ml.constants import CREATE_ENVIRONMENT_ERROR_MESSAGE, YAMLRefDocLinks, ANONYMOUS_ENV_NAME

module_logger = logging.getLogger(__name__)


class BuildContextSchema(metaclass=PatchedSchemaMeta):
    dockerfile_path = fields.Str()
    path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets.environment import BuildContext

        return BuildContext(**data)


class RouteSchema(metaclass=PatchedSchemaMeta):
    port = fields.Int(required=True)
    path = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        return Route(**data)


class InferenceConfigSchema(metaclass=PatchedSchemaMeta):
    liveness_route = NestedField(RouteSchema, required=True)
    scoring_route = NestedField(RouteSchema, required=True)
    readiness_route = NestedField(RouteSchema, required=True)

    @post_load
    def make(self, data, **kwargs):
        return InferenceContainerProperties(**data)


class _BaseEnvironmentSchema(AssetSchema):
    id = UnionField(
        [
            RegistryStr(dump_only=True),
            ArmStr(azureml_type=AzureMLResourceType.ENVIRONMENT, dump_only=True),
        ]
    )
    build = NestedField(
        BuildContextSchema,
        metadata={"description": "Docker build context to create the environment. Mutually exclusive with image"},
    )
    image = fields.Str()
    conda_file = UnionField([fields.Raw(), fields.Str()])
    inference_config = NestedField(InferenceConfigSchema)
    os_type = StringTransformedEnum(
        allowed_values=[OperatingSystemType.Linux, OperatingSystemType.Windows], required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @pre_load
    def pre_load(self, data, **kwargs):
        if isinstance(data, str):
            raise ValidationError("Environment schema data cannot be a string")
        # validates that "channels" and "dependencies" are not included in the data creation.
        # These properties should only be on environment conda files not in the environment creation file
        if "channels" in data or "dependencies" in data:
            environmentMessage = CREATE_ENVIRONMENT_ERROR_MESSAGE.format(YAMLRefDocLinks.ENVIRONMENT)
            raise ValidationError(environmentMessage)
        return data

    @pre_dump
    def validate(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Environment

        if isinstance(data, Environment):
            return data
        if data is None or not hasattr(data, "get"):
            raise ValidationError("Environment cannot be None")
        return data

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import Environment

        try:
            obj = Environment(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
        except FileNotFoundError as e:
            # Environment.__init__() will raise FileNotFoundError if build.path is not found when trying to calculate
            # the hash for anonymous. Raise ValidationError instead to collect all errors in schema validation.
            raise ValidationError("Environment file not found: {}".format(e))
        return obj


class EnvironmentSchema(_BaseEnvironmentSchema):
    name = fields.Str(required=True)
    version = VersionField()


class AnonymousEnvironmentSchema(_BaseEnvironmentSchema, AnonymousAssetSchema):
    @pre_load
    def trim_dump_only(self, data, **kwargs):
        """
        trim_dump_only in PathAwareSchema removes all properties which are dump only. By the time we reach this
        schema name and version properties are removed so no warning is shown. This method overrides trim_dump_only
        in PathAwareSchema to check for name and version and raise warning if present. And then calls the it
        """
        if isinstance(data, str) or data is None:
            return data
        name = data.pop("name", None)
        data.pop("version", None)
        # CliV2AnonymousEnvironment is a default name for anonymous environment
        if name is not None and name != ANONYMOUS_ENV_NAME:
            module_logger.warning(
                f"Warning: the provided asset name '{name}' will not be used for anonymous " f"registration"
            )
        return super(AnonymousEnvironmentSchema, self).trim_dump_only(data, **kwargs)
