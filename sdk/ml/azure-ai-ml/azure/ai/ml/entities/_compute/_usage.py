# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_01_01_preview.models import Usage as RestUsage, UsageName as RestUsageName, UsageUnit
from azure.ai.ml._schema.compute.usage import UsageSchema
from azure.ai.ml.entities import Resource
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from typing import Dict, Union
from os import PathLike
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    CommonYamlFields,
)


class UsageName:
    def __init__(self, *, value: str = None, localized_value: str = None, **kwargs):
        """The Usage Names.

        :param value: The name of the resource.
        :type value: str
        :param localized_value: The localized name of the resource.
        :type localized_value: str
        """
        self.value = value
        self.localized_value = localized_value


class Usage(Resource, RestTranslatableMixin):
    """Describes AML Resource Usage"""

    def __init__(
        self,
        id: str = None,
        aml_workspace_location: str = None,
        type: str = None,
        unit: Union[str, UsageUnit] = None,  # enum
        current_value: int = None,
        limit: int = None,
        name: RestUsageName = None,
        **kwargs,
    ):
        """Describes AML Resource Usage
        :param id: Specifies the resource ID.
        :type id: str
        :param aml_workspace_location: Region of the AML workspace in the id.
        :type aml_workspace_location: str
        :param type: Specifies the resource type.
        :type type: str
        :param unit: An enum describing the unit of usage measurement. Possible values include: "Count".
        :type unit: str or ~azure.mgmt.machinelearningservices.models.UsageUnit
        :param current_value: The current usage of the resource.
        :type current_value: int
        :param limit: The maximum permitted usage of the resource.
        :type limit: int
        :param name: The name of the type of usage.
        :type name: ~azure.mgmt.machinelearningservices.models.UsageName
        """

        self.aml_workspace_location = aml_workspace_location
        self.type = type
        self.unit = unit
        self.current_value = current_value
        self.limit = limit
        self.name = name

    @classmethod
    def _from_rest_object(cls, rest_obj: RestUsage) -> "Usage":
        result = cls()
        result.__dict__.update(rest_obj.as_dict())
        return result

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the resourse usage content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return UsageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Usage":

        pass
