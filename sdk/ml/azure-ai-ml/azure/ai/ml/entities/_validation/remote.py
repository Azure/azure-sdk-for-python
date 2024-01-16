# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
import typing

import msrest

from azure.ai.ml._vendor.azure_resources.models import (
    Deployment,
    DeploymentProperties,
    DeploymentValidateResult,
    ErrorResponse,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin

from .core import MutableValidationResult, ValidationResultBuilder

module_logger = logging.getLogger(__name__)


class PreflightResource(msrest.serialization.Model):
    """Specified resource.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Resource ID.
    :vartype id: str
    :ivar name: Resource name.
    :vartype name: str
    :ivar type: Resource type.
    :vartype type: str
    :param location: Resource location.
    :type location: str
    :param tags: A set of tags. Resource tags.
    :type tags: dict[str, str]
    """

    _attribute_map = {
        "type": {"key": "type", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "location": {"key": "location", "type": "str"},
        "api_version": {"key": "apiversion", "type": "str"},
        "properties": {"key": "properties", "type": "object"},
    }

    def __init__(self, **kwargs: typing.Any):
        super(PreflightResource, self).__init__(**kwargs)
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.location = kwargs.get("location", None)
        self.properties = kwargs.get("properties", None)
        self.api_version = kwargs.get("api_version", None)


class ValidationTemplateRequest(msrest.serialization.Model):
    """Export resource group template request parameters.

    :param resources: The rest objects to be validated.
    :type resources: list[_models.Resource]
    :param options: The export template options. A CSV-formatted list containing zero or more of
     the following: 'IncludeParameterDefaultValue', 'IncludeComments',
     'SkipResourceNameParameterization', 'SkipAllParameterization'.
    :type options: str
    """

    _attribute_map = {
        "resources": {"key": "resources", "type": "[PreflightResource]"},
        "content_version": {"key": "contentVersion", "type": "str"},
        "parameters": {"key": "parameters", "type": "object"},
        "_schema": {
            "key": "$schema",
            "type": "str",
            "default": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        },
    }

    def __init__(self, **kwargs: typing.Any):
        super(ValidationTemplateRequest, self).__init__(**kwargs)
        self._schema = kwargs.get("_schema", None)
        self.content_version = kwargs.get("content_version", None)
        self.parameters = kwargs.get("parameters", None)
        self.resources = kwargs.get("resources", None)


class RemoteValidatableMixin(RestTranslatableMixin):
    @classmethod
    def _get_resource_type(cls) -> str:
        """Return resource type to be used in remote validation.

        Should be overridden by subclass.

        :return: The resource type
        :rtype: str
        """
        raise NotImplementedError()

    def _get_resource_name_version(self) -> typing.Tuple:
        """Return resource name and version to be used in remote validation.

        Should be overridden by subclass.

        :return: The name and version
        :rtype: typing.Tuple[str, str]
        """
        raise NotImplementedError()

    def _to_preflight_resource(self, location: str, workspace_name: str) -> PreflightResource:
        """Return the preflight resource to be used in remote validation.

        :param location: The location of the resource.
        :type location: str
        :param workspace_name: The workspace name
        :type workspace_name: str
        :return: The preflight resource
        :rtype: PreflightResource
        """
        name, version = self._get_resource_name_version()
        return PreflightResource(
            type=self._get_resource_type(),
            name=f"{workspace_name}/{name}/{version}",
            location=location,
            properties=self._to_rest_object().properties,
            api_version="2023-03-01-preview",
        )

    def _build_rest_object_for_remote_validation(self, location: str, workspace_name: str) -> Deployment:
        return Deployment(
            properties=DeploymentProperties(
                mode="Incremental",
                template=ValidationTemplateRequest(
                    _schema="https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                    content_version="1.0.0.0",
                    parameters={},
                    resources=[self._to_preflight_resource(location=location, workspace_name=workspace_name)],
                ),
            )
        )

    @classmethod
    def _build_validation_result_from_rest_object(cls, rest_obj: DeploymentValidateResult) -> MutableValidationResult:
        """Create a validation result from a rest object. Note that the created validation result does not have
        target_obj so should only be used for merging.

        :param rest_obj: The Deployment Validate REST obj
        :type rest_obj: DeploymentValidateResult
        :return: The validation result created from rest_obj
        :rtype: MutableValidationResult
        """
        if not rest_obj.error or not rest_obj.error.details:
            return ValidationResultBuilder.success()
        result = MutableValidationResult(target_obj=None)
        details: typing.List[ErrorResponse] = rest_obj.error.details
        for detail in details:
            result.append_error(
                message=detail.message,
                yaml_path=detail.target.replace("/", "."),
                error_code=detail.code,
                # will always be UserError for now, not sure if innerError can be passed back
            )
        return result
