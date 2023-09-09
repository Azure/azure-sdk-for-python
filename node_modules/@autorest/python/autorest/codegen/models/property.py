# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Optional, TYPE_CHECKING, List

from .base import BaseModel
from .constant_type import ConstantType
from .base import BaseType
from .imports import FileImport, ImportType
from .utils import add_to_description, add_to_pylint_disable

if TYPE_CHECKING:
    from .code_model import CodeModel
    from .model_type import ModelType


class Property(BaseModel):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        type: BaseType,
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.wire_name: str = self.yaml_data["wireName"]
        self.client_name: str = self.yaml_data["clientName"]
        self.type = type
        self.optional: bool = self.yaml_data["optional"]
        self.readonly: bool = self.yaml_data.get("readonly", False)
        self.visibility: List[str] = self.yaml_data.get("visibility", [])
        self.is_polymorphic: bool = self.yaml_data.get("isPolymorphic", False)
        self.is_discriminator: bool = yaml_data.get("isDiscriminator", False)
        self.client_default_value = yaml_data.get("clientDefaultValue", None)
        if self.client_default_value is None:
            self.client_default_value = self.type.client_default_value
        self.flattened_names: List[str] = yaml_data.get("flattenedNames", [])

    @property
    def pylint_disable(self) -> str:
        retval: str = ""
        if self.yaml_data.get("pylintDisable"):
            retval = add_to_pylint_disable(retval, self.yaml_data["pylintDisable"])
        return retval

    def description(self, *, is_operation_file: bool) -> str:
        from .model_type import ModelType

        description = self.yaml_data.get("description", "")
        if not (self.optional or self.client_default_value):
            description = add_to_description(description, "Required.")
        # don't want model type documentation as part of property doc
        type_description = (
            ""
            if isinstance(self.type, ModelType)
            else self.type.description(is_operation_file=is_operation_file)
        )
        return add_to_description(description, type_description)

    @property
    def client_default_value_declaration(self) -> str:
        if self.client_default_value is not None:
            return self.type.get_declaration(self.client_default_value)
        if self.type.client_default_value is not None:
            return self.type.get_declaration(self.type.client_default_value)
        return "None"

    @property
    def constant(self) -> bool:
        # this bool doesn't consider you to be constant if you are a discriminator
        # you also have to be required to be considered a constant
        return (
            isinstance(self.type, ConstantType)
            and not self.optional
            and not self.is_discriminator
        )

    @property
    def is_input(self):
        return not (self.constant or self.readonly or self.is_discriminator)

    @property
    def serialization_type(self) -> str:
        return self.type.serialization_type

    @property
    def msrest_deserialization_key(self) -> str:
        return self.type.msrest_deserialization_key

    def type_annotation(self, *, is_operation_file: bool = False) -> str:
        if self.optional and self.client_default_value is None:
            return f"Optional[{self.type.type_annotation(is_operation_file=is_operation_file)}]"
        return self.type.type_annotation(is_operation_file=is_operation_file)

    def get_json_template_representation(
        self,
        *,
        optional: bool = True,  # pylint: disable=unused-argument
        client_default_value_declaration: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        if self.client_default_value:
            client_default_value_declaration = self.type.get_declaration(
                self.client_default_value
            )
        if self.description(is_operation_file=True):
            description = self.description(is_operation_file=True)
        return self.type.get_json_template_representation(
            optional=self.optional,
            client_default_value_declaration=client_default_value_declaration,
            description=description,
        )

    def get_polymorphic_subtypes(self, polymorphic_subtypes: List["ModelType"]) -> None:
        from .model_type import ModelType

        if isinstance(self.type, ModelType):
            self.type.get_polymorphic_subtypes(polymorphic_subtypes)

    @property
    def validation(self) -> Optional[Dict[str, Any]]:
        retval: Dict[str, Any] = {}
        if not self.optional:
            retval["required"] = True
        if self.readonly:
            retval["readonly"] = True
        if self.constant:
            retval["constant"] = True
        retval.update(self.type.validation or {})
        return retval or None

    def imports(self, **kwargs) -> FileImport:
        file_import = self.type.imports(**kwargs, relative_path="..", model_typing=True)
        if self.optional and self.client_default_value is None:
            file_import.add_submodule_import("typing", "Optional", ImportType.STDLIB)
        if self.code_model.options["models_mode"] == "dpg":
            file_import.add_submodule_import(
                ".._model_base",
                "rest_discriminator" if self.is_discriminator else "rest_field",
                ImportType.LOCAL,
            )
        return file_import

    @classmethod
    def from_yaml(
        cls,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
    ) -> "Property":
        from . import build_type  # pylint: disable=import-outside-toplevel

        return cls(
            yaml_data=yaml_data,
            code_model=code_model,
            type=build_type(yaml_data["type"], code_model),
        )
