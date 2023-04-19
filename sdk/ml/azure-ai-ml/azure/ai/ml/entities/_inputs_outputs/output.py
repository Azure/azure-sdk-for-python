# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin, too-many-instance-attributes
import re
from typing import Dict, overload

from typing_extensions import Literal

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.exceptions import UserErrorException
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty

from .base import _InputOutputBase
from .utils import _remove_empty_values


class Output(_InputOutputBase):
    """Define an output of a Component or Job.

    :param type: The type of the data output. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
    :type type: str
    :param path: The path to which the output is pointing. Needs to point to a cloud path.
    :type path: str
    :param mode: The mode of the data output. Possible values are:
                        'rw_mount': Read-write mount the data,
                        'upload': Upload the data from the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param description: Description of the output
    :type description: str
    :param name: The name used to register output as data or model asset. Name can be set without setting version.
    :type name: str
    :param version: The version used to register output as data or model asset.
        Version can be set only when name is set.
    :type version: str
    """

    @overload
    def __init__(self, type: Literal["uri_folder"] = "uri_folder", path=None, mode=None, description=None):
        """Define a uri_folder output.

        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        :param name: The name used to register output as data or model asset. Name can be set without setting version.
        :type name: str
        :param version: The version used to register output as data or model asset.
            Version can be set only when name is set.
        :type version: str
        """

    @overload
    def __init__(self, type: Literal["uri_file"] = "uri_file", path=None, mode=None, description=None):
        """Define a uri_file output.

        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        :param name: The name used to register output as data or model asset. Name can be set without setting version.
        :type name: str
        :param version: The version used to register output as data or model asset.
            Version can be set only when name is set.
        :type version: str
        """

    def __init__(self, *, type=AssetTypes.URI_FOLDER, path=None, mode=None, description=None, **kwargs):
        super(Output, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the _port_name.
        self._port_name = None
        self.name = kwargs.pop("name", None)
        self.version = kwargs.pop("version", None)
        self._is_primitive_type = self.type in IOConstants.PRIMITIVE_STR_2_TYPE
        self.description = description
        self.path = path
        self.mode = mode
        # use this field to determine the Output is control or not, currently hide in kwargs
        self.is_control = kwargs.pop("is_control", None)
        # use this field to mark Output for early node orchestrate, currently hide in kwargs
        self.early_available = kwargs.pop("early_available", None)
        self._intellectual_property = None
        intellectual_property = kwargs.pop("intellectual_property", None)
        if intellectual_property:
            self._intellectual_property = (
                intellectual_property
                if isinstance(intellectual_property, IntellectualProperty)
                else IntellectualProperty(**intellectual_property)
            )
        self._assert_name_and_version()
        # normalize properties like ["is_control"]
        self._normalize_self_properties()

    def _get_hint(self, new_line_style=False):
        comment_str = self.description.replace('"', '\\"') if self.description else self.type
        return '"""%s"""' % comment_str if comment_str and new_line_style else comment_str

    def _to_dict(self):
        """Convert the Output object to a dict."""
        keys = ["name", "version", "path", "type", "mode", "description", "is_control", "early_available"]
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)

    def _to_rest_object(self) -> Dict:
        # this is for component rest object when using Output as component outputs, as for job output usage,
        # rest object is generated by extracting Output's properties, see details in to_rest_data_outputs()
        return self._to_dict()

    def _simple_parse(self, value, _type=None):
        if _type is None:
            _type = self.type
        if _type in IOConstants.PARAM_PARSERS:
            return IOConstants.PARAM_PARSERS[_type](value)
        return value

    def _normalize_self_properties(self):
        # parse value from string to its original type. eg: "false" -> False
        if self.is_control:
            self.is_control = self._simple_parse(getattr(self, "is_control", "false"), _type="boolean")
        if self.early_available:
            self.early_available = self._simple_parse(getattr(self, "early_available", "false"), _type="boolean")

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Output":
        # this is for component rest object when using Output as component outputs
        return Output(**obj)

    def _assert_name_and_version(self):
        if self.name and not (re.match("^[A-Za-z0-9_-]*$", self.name) and len(self.name) <= 255):
            raise UserErrorException(
                f"The output name {self.name} can only contain alphanumeric characters, dashes and underscores, "
                f"with a limit of 255 characters."
            )
        if self.version and not self.name:
            raise UserErrorException("Output name is required when output version is specified.")
