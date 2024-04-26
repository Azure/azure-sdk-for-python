# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import Usage as RestUsage
from azure.ai.ml._restclient.v2022_10_01_preview.models import UsageUnit
from azure.ai.ml._schema.compute.usage import UsageSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class UsageName:
    def __init__(self, *, value: Optional[str] = None, localized_value: Optional[str] = None) -> None:
        """The usage name.

        :param value: The name of the resource.
        :type value: Optional[str]
        :param localized_value: The localized name of the resource.
        :type localized_value: Optional[str]
        """
        self.value = value
        self.localized_value = localized_value


class Usage(RestTranslatableMixin):
    """AzureML resource usage.

    :param id: The resource ID.
    :type id: Optional[str]
    :param aml_workspace_location: The region of the AzureML workspace specified by the ID.
    :type aml_workspace_location: Optional[str]
    :param type: The resource type.
    :type type: Optional[str]
    :param unit: The unit of measurement for usage. Accepted value is "Count".
    :type unit: Optional[Union[str, ~azure.ai.ml.entities.UsageUnit]]
    :param current_value: The current usage of the resource.
    :type current_value: Optional[int]
    :param limit: The maximum permitted usage for the resource.
    :type limit: Optional[int]
    :param name: The name of the usage type.
    :type name: Optional[~azure.ai.ml.entities.UsageName]
    """

    def __init__(
        self,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        aml_workspace_location: Optional[str] = None,
        type: Optional[str] = None,  # pylint: disable=redefined-builtin
        unit: Optional[Union[str, UsageUnit]] = None,  # enum
        current_value: Optional[int] = None,
        limit: Optional[int] = None,
        name: Optional[UsageName] = None,
    ) -> None:
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

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dumps the job content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises: FileExistsError if dest is a file path and the file already exists.
        :raises: IOError if dest is an open file and the file is not writable.
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = UsageSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    @abstractmethod
    def _load(
        cls,
        path: Union[PathLike, str],
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Usage":
        pass
