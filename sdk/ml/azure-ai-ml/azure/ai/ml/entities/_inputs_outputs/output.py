# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin, too-many-instance-attributes
import re
from typing import Dict, overload

from typing_extensions import Literal

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.exceptions import UserErrorException

from .base import _InputOutputBase
from .utils import _remove_empty_values


class Output(_InputOutputBase):
    _IO_KEYS = ["name", "version", "path", "type", "mode", "description", "early_available"]

    @overload
    def __init__(self, type: Literal["uri_folder"] = "uri_folder", path=None, mode=None, description=None) -> None:
        # pylint: disable=line-too-long
        """Define an output.

        :keyword type: The type of the data output. Accepted values are 'uri_folder', 'uri_file', 'mltable',
            'mlflow_model', 'custom_model', and user-defined types. Defaults to 'uri_folder'.
        :paramtype type: str
        :keyword path: The remote path where the output should be stored.
        :paramtype path: Optional[str]
        :keyword mode: The access mode of the data output. Accepted values are
            * 'rw_mount': Read-write mount the data
            * 'upload': Upload the data from the compute target
            * 'direct': Pass in the URI as a string
        :paramtype mode: Optional[str]
        :keyword description: The description of the output.
        :paramtype description: Optional[str]
        :keyword name: The name to be used to register the output as a Data or Model asset. A name can be set without
            setting a version.
        :paramtype name: str
        :keyword version: The version used to register the output as a Data or Model asset. A version can be set only
            when name is set.
        :paramtype version: str
        :keyword is_control: Determine if the output is a control output.
        :paramtype is_control: bool
        :keyword early_available: Mark the output for early node orchestration.
        :paramtype early_available: bool
        :keyword intellectual_property: Intellectual property associated with the output.
            It can be an instance of `IntellectualProperty` or a dictionary that will be used to create an instance.
        :paramtype intellectual_property: Union[~azure.ai.ml.entities._assets.intellectual_property.IntellectualProperty,

            dict]

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_misc.py
                :start-after: [START create_inputs_outputs]
                :end-before: [END create_inputs_outputs]
                :language: python
                :dedent: 8
                :caption: Creating a CommandJob with a folder output.
        """

    @overload
    def __init__(self, type: Literal["uri_file"] = "uri_file", path=None, mode=None, description=None):
        """Define a URI file output.

        :keyword type: The type of the data output. Can only be set to 'uri_file'.
        :paramtype type: str
        :keyword path: The remote path where the output should be stored.
        :paramtype path: str
        :keyword mode: The access mode of the data output. Accepted values are
            * 'rw_mount': Read-write mount the data,
            * 'upload': Upload the data from the compute target,
            * 'direct': Pass in the URI as a string
        :paramtype mode: str
        :keyword description: The description of the output.
        :paramtype description: str
        :keyword name: The name to be used to register the output as a Data or Model asset. A name can be set without
            setting a version.
        :paramtype name: str
        :keyword version: The version used to register the output as a Data or Model asset. A version can be set only
            when name is set.
        :paramtype version: str
        """

    def __init__(self, *, type=AssetTypes.URI_FOLDER, path=None, mode=None, description=None, **kwargs) -> None:
        super(Output, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the _port_name.
        self._port_name = None
        self.name = kwargs.pop("name", None)
        self.version = kwargs.pop("version", None)
        self._is_primitive_type = self.type in IOConstants.PRIMITIVE_STR_2_TYPE
        self.description = description
        self.path = path
        self.mode = mode
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
        # normalize properties
        self._normalize_self_properties()

    def _get_hint(self, new_line_style=False):
        comment_str = self.description.replace('"', '\\"') if self.description else self.type
        return '"""%s"""' % comment_str if comment_str and new_line_style else comment_str

    def _to_dict(self) -> Dict:
        """Convert the Output object to a dict.

        :return: The dictionary representation of Output
        :rtype: Dict
        """
        keys = self._IO_KEYS
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
