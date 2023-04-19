# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import IO, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import Usage as RestUsage
from azure.ai.ml._restclient.v2022_10_01_preview.models import UsageUnit
from azure.ai.ml._schema.compute.usage import UsageSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class UsageName:
    def __init__(self, *, value: Optional[str] = None, localized_value: Optional[str] = None):
        """The Usage Names.

        :param value: The name of the resource.
        :type value: str
        :param localized_value: The localized name of the resource.
        :type localized_value: str
        """
        self.value = value
        self.localized_value = localized_value


class Usage(RestTranslatableMixin):
    """Describes AML Resource Usage."""

    def __init__(
        self,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        aml_workspace_location: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        unit: Optional[Union[str, UsageUnit]] = None,  # enum
        current_value: Optional[int] = None,
        limit: Optional[int] = None,
        name: Optional[UsageName] = None,
    ):
        """Describes AML Resource Usage.

        :param id: Specifies the resource ID.
        :type id: str
        :param aml_workspace_location: Region of the AML workspace in the id.
        :type aml_workspace_location: str
        :param type: Specifies the resource type.
        :type type: str
        :param unit: An enum describing the unit of usage measurement. Possible values include: "Count".
        :type unit: str or ~azure.ai.ml.entities.UsageUnit
        :param current_value: The current usage of the resource.
        :type current_value: int
        :param limit: The maximum permitted usage of the resource.
        :type limit: int
        :param name: The name of the type of usage.
        :type name: ~azure.ai.ml.entities.UsageName
        """
        self.id = id
        self.aml_workspace_location = aml_workspace_location
        self.type = type
        self.unit = unit
        self.current_value = current_value
        self.limit = limit
        self.name = name

    @classmethod
    def _from_rest_object(cls, obj: RestUsage) -> "Usage":
        result = cls()
        result.__dict__.update(obj.as_dict())
        return result

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the resource usage content into a file in yaml format.

        :param dest: The destination to receive this resource usage's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return UsageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        path: Union[PathLike, str],
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Usage":
        pass
