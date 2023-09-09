# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import abc
from enum import Enum

from typing import (
    Dict,
    Any,
    TYPE_CHECKING,
    List,
    Optional,
    TypeVar,
    Union,
    Generic,
)

from .imports import FileImport, ImportType, TypingSection
from .base import BaseModel
from .base import BaseType
from .constant_type import ConstantType
from .utils import add_to_description
from .combined_type import CombinedType
from .model_type import JSONModelType

if TYPE_CHECKING:
    from .code_model import CodeModel
    from .request_builder_parameter import RequestBuilderBodyParameter


class ParameterLocation(str, Enum):
    HEADER = "header"
    PATH = "path"
    ENDPOINT_PATH = "endpointPath"
    QUERY = "query"
    BODY = "body"
    OTHER = "other"


class ParameterMethodLocation(str, Enum):
    POSITIONAL = "positional"
    KEYWORD_ONLY = "keywordOnly"
    KWARG = "kwarg"


class ParameterDelimeter(str, Enum):
    SPACE = "space"
    PIPE = "pipe"
    TAB = "tab"
    COMMA = "comma"


class _ParameterBase(
    BaseModel, abc.ABC
):  # pylint: disable=too-many-instance-attributes
    """Base class for all parameters"""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        type: BaseType,
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.wire_name: str = yaml_data["wireName"]
        self.client_name: str = self.yaml_data["clientName"]
        self.optional: bool = self.yaml_data["optional"]
        self.location: ParameterLocation = self.yaml_data["location"]
        self.client_default_value = self.yaml_data.get("clientDefaultValue", None)
        self.in_docstring = self.yaml_data.get("inDocstring", True)
        self.type = type
        if self.client_default_value is None:
            self.client_default_value = self.type.client_default_value
        # name of grouper if it is grouped by another parameter
        self.grouped_by: Optional[str] = self.yaml_data.get("groupedBy")
        # property matching property name to parameter name for grouping params
        # and flattened body params
        self.property_to_parameter_name: Optional[Dict[str, str]] = self.yaml_data.get(
            "propertyToParameterName"
        )
        self.flattened: bool = self.yaml_data.get("flattened", False)
        self.in_flattened_body: bool = self.yaml_data.get("inFlattenedBody", False)
        self.grouper: bool = self.yaml_data.get("grouper", False)
        self.check_client_input: bool = self.yaml_data.get("checkClientInput", False)
        self.added_on: Optional[str] = self.yaml_data.get("addedOn")
        self.is_api_version: bool = self.yaml_data.get("isApiVersion", False)
        self.in_overload: bool = self.yaml_data.get("inOverload", False)
        self.default_to_unset_sentinel: bool = self.yaml_data.get(
            "defaultToUnsetSentinel", False
        )
        self.hide_in_method: bool = self.yaml_data.get("hideInMethod", False)

    @property
    def constant(self) -> bool:
        """Returns whether a parameter is a constant or not.
        Checking to see if it's required, because if not, we don't consider it
        a constant because it can have a value of None.
        """
        return (not self.optional or self.is_api_version) and isinstance(
            self.type, ConstantType
        )

    @property
    def description(self) -> str:
        base_description = self.yaml_data["description"]
        type_description = self.type.description(is_operation_file=True)
        if type_description:
            base_description = add_to_description(base_description, type_description)
        if self.optional and isinstance(self.type, ConstantType):
            base_description = add_to_description(
                base_description,
                f"Known values are {self.type.get_declaration()} and None.",
            )
        if not (self.optional or self.client_default_value):
            base_description = add_to_description(base_description, "Required.")
        if self.client_default_value is not None:
            base_description = add_to_description(
                base_description,
                f"Default value is {self.client_default_value_declaration}.",
            )
        if self.optional and self.client_default_value is None:
            base_description = add_to_description(
                base_description,
                f"Default value is {self.client_default_value_declaration}.",
            )
        if self.constant:
            base_description = add_to_description(
                base_description,
                "Note that overriding this default value may result in unsupported behavior.",
            )
        return base_description

    @property
    def client_default_value_declaration(self):
        """Declaration of parameter's client default value"""
        if self.client_default_value is None:
            return None
        return self.type.get_declaration(self.client_default_value)

    def type_annotation(self, **kwargs: Any) -> str:
        kwargs["is_operation_file"] = True
        # special logic for api-version parameter
        if self.is_api_version:
            type_annot = "str"
        else:
            type_annot = self.type.type_annotation(**kwargs)
        if self.optional and self.client_default_value is None:
            return f"Optional[{type_annot}]"
        return type_annot

    def docstring_text(self, **kwargs: Any) -> str:
        return self.type.docstring_text(**kwargs)

    def docstring_type(self, **kwargs: Any) -> str:
        return self.type.docstring_type(**kwargs)

    @property
    def serialization_type(self) -> str:
        return self.type.serialization_type

    def _imports_shared(self, async_mode: bool, **_: Any) -> FileImport:
        file_import = FileImport()
        if self.optional and self.client_default_value is None:
            file_import.add_submodule_import("typing", "Optional", ImportType.STDLIB)
        if self.added_on:
            file_import.add_submodule_import(
                f"{'.' if async_mode else ''}.._validation",
                "api_version_validation",
                ImportType.LOCAL,
            )
        if isinstance(self.type, CombinedType) and self.type.name:
            file_import.add_submodule_import(
                "..",
                "_types",
                ImportType.LOCAL,
                TypingSection.TYPING,
            )
        return file_import

    def imports(self, async_mode: bool, **kwargs: Any) -> FileImport:
        file_import = self._imports_shared(async_mode, **kwargs)
        # special logic for api-version parameter
        if not self.is_api_version:
            file_import.merge(self.type.imports(async_mode=async_mode, **kwargs))
        if self.default_to_unset_sentinel:
            file_import.add_submodule_import("typing", "Any", ImportType.STDLIB)
            file_import.define_mypy_type(
                "_Unset: Any",
                "object()",
            )
        return file_import

    def imports_for_multiapi(self, async_mode: bool, **kwargs: Any) -> FileImport:
        file_import = self._imports_shared(async_mode, **kwargs)
        file_import.merge(
            self.type.imports_for_multiapi(async_mode=async_mode, **kwargs)
        )
        return file_import

    @property
    def method_location(self) -> ParameterMethodLocation:
        raise NotImplementedError("Please implement in children")

    @property
    def description_keyword(self) -> str:
        return (
            "param"
            if self.method_location == ParameterMethodLocation.POSITIONAL
            else "keyword"
        )

    @property
    def docstring_type_keyword(self) -> str:
        return (
            "type"
            if self.method_location == ParameterMethodLocation.POSITIONAL
            else "paramtype"
        )

    @property
    @abc.abstractmethod
    def in_method_signature(self) -> bool:
        ...

    def method_signature(self, async_mode: bool) -> str:
        type_annot = self.type_annotation(async_mode=async_mode)
        if self.client_default_value is not None or self.optional:
            return f"{self.client_name}: {type_annot} = {self.client_default_value_declaration},"
        if self.default_to_unset_sentinel:
            return f"{self.client_name}: {type_annot} = _Unset,"
        return f"{self.client_name}: {type_annot},"


class BodyParameter(_ParameterBase):
    """Body parameter."""

    @property
    def is_partial_body(self) -> bool:
        """Whether it's part of a bigger body parameter, i.e. a MultipartBodyParameter"""
        return self.yaml_data.get("isPartialBody", False)

    @property
    def method_location(self) -> ParameterMethodLocation:
        return (
            ParameterMethodLocation.KWARG
            if self.constant
            else ParameterMethodLocation.POSITIONAL
        )

    @property
    def in_method_signature(self) -> bool:
        return not (self.flattened or self.grouped_by)

    @property
    def content_types(self) -> List[str]:
        return self.yaml_data["contentTypes"]

    @property
    def default_content_type(self) -> str:
        return self.yaml_data["defaultContentType"]

    @property
    def has_json_model_type(self) -> bool:
        if isinstance(self.type, CombinedType):
            return self.type.json_subtype is not None
        return isinstance(self.type, JSONModelType)

    @classmethod
    def from_yaml(
        cls, yaml_data: Dict[str, Any], code_model: "CodeModel"
    ) -> "BodyParameter":
        return cls(
            yaml_data=yaml_data,
            code_model=code_model,
            type=code_model.lookup_type(id(yaml_data["type"])),
        )


EntryBodyParameterType = TypeVar(
    "EntryBodyParameterType", bound=Union[BodyParameter, "RequestBuilderBodyParameter"]
)


class _MultipartBodyParameter(Generic[EntryBodyParameterType], BodyParameter):
    """Base class for MultipartBodyParameter and RequestBuilderMultipartBodyParameter"""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        type: BaseType,
        entries: List[EntryBodyParameterType],
    ) -> None:
        super().__init__(yaml_data, code_model, type)
        self.entries = entries

    @property
    def in_method_signature(self) -> bool:
        # Right now, only legacy generates with multipart bodies
        # and legacy generates with the multipart body arguments splatted out
        return False


class MultipartBodyParameter(
    _MultipartBodyParameter[BodyParameter]  # pylint: disable=unsubscriptable-object
):
    """Multipart body parameter for Operation. Used for files and data input."""

    @classmethod
    def from_yaml(
        cls, yaml_data: Dict[str, Any], code_model: "CodeModel"
    ) -> "MultipartBodyParameter":
        return cls(
            yaml_data=yaml_data,
            code_model=code_model,
            type=code_model.lookup_type(id(yaml_data["type"])),
            entries=[
                BodyParameter.from_yaml(entry, code_model)
                for entry in yaml_data["entries"]
            ],
        )


class Parameter(_ParameterBase):
    """Basic Parameter class"""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        type: BaseType,
    ) -> None:
        super().__init__(yaml_data, code_model, type=type)

        self.implementation: str = yaml_data["implementation"]
        self.skip_url_encoding: bool = self.yaml_data.get("skipUrlEncoding", False)
        self.explode: bool = self.yaml_data.get("explode", False)
        self.in_overriden: bool = self.yaml_data.get("inOverriden", False)
        self.delimiter: Optional[ParameterDelimeter] = self.yaml_data.get("delimiter")
        self._default_to_unset_sentinel: bool = False

    @property
    def in_method_signature(self) -> bool:
        return not (self.wire_name == "Accept" or self.grouped_by or self.flattened)

    @property
    def full_client_name(self) -> str:
        if self.implementation == "Client":
            return f"self._config.{self.client_name}"
        return self.client_name

    @property
    def xml_serialization_ctxt(self) -> str:
        return self.type.xml_serialization_ctxt or ""

    @property
    def is_content_type(self) -> bool:
        return bool(self.wire_name) and self.wire_name.lower() == "content-type"

    @property
    def method_location(  # pylint: disable=too-many-return-statements
        self,
    ) -> ParameterMethodLocation:
        if not self.in_method_signature:
            raise ValueError(f"Parameter '{self.client_name}' is not in the method.")
        if self.code_model.options["models_mode"] == "dpg" and self.in_flattened_body:
            return ParameterMethodLocation.KEYWORD_ONLY
        if self.grouper:
            return ParameterMethodLocation.POSITIONAL
        if self.constant:
            return ParameterMethodLocation.KWARG
        if self.is_content_type:
            if self.in_overload:
                return ParameterMethodLocation.KEYWORD_ONLY
            return ParameterMethodLocation.KWARG
        query_or_header = self.location in (
            ParameterLocation.HEADER,
            ParameterLocation.QUERY,
        )
        if (
            self.code_model.options["only_path_and_body_params_positional"]
            and query_or_header
        ):
            return ParameterMethodLocation.KEYWORD_ONLY
        return ParameterMethodLocation.POSITIONAL

    @classmethod
    def from_yaml(cls, yaml_data: Dict[str, Any], code_model: "CodeModel"):
        return cls(
            yaml_data=yaml_data,
            code_model=code_model,
            type=code_model.lookup_type(id(yaml_data["type"])),
        )


class ClientParameter(Parameter):
    """Client parameter"""

    @property
    def is_host(self) -> bool:
        return self.wire_name == "$host"

    @property
    def method_location(self) -> ParameterMethodLocation:
        if self.constant:
            return ParameterMethodLocation.KWARG
        if self.is_host and (
            self.code_model.options["version_tolerant"]
            or self.code_model.options["low_level_client"]
        ):
            # this means i am the base url
            return ParameterMethodLocation.KEYWORD_ONLY
        return ParameterMethodLocation.POSITIONAL


class ConfigParameter(Parameter):
    """Config Parameter"""

    @property
    def in_method_signature(self) -> bool:
        return not self.is_host

    @property
    def is_host(self) -> bool:
        return self.wire_name == "$host"

    @property
    def method_location(self) -> ParameterMethodLocation:
        if self.constant:
            return ParameterMethodLocation.KWARG
        return ParameterMethodLocation.POSITIONAL


def get_body_parameter(
    yaml_data: Dict[str, Any], code_model: "CodeModel"
) -> Union[BodyParameter, MultipartBodyParameter]:
    """Creates a regular body parameter or Multipart body parameter"""
    if yaml_data.get("entries"):
        return MultipartBodyParameter.from_yaml(yaml_data, code_model)
    return BodyParameter.from_yaml(yaml_data, code_model)
