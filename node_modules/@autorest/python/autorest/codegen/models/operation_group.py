# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Dict, List, Any, TYPE_CHECKING

from autorest.codegen.models.utils import OrderedSet

from .base import BaseModel
from .operation import get_operation
from .imports import FileImport, ImportType, TypingSection
from .utils import add_to_pylint_disable, NAME_LENGTH_LIMIT

if TYPE_CHECKING:
    from .code_model import CodeModel
    from .client import Client
    from . import OperationType


class OperationGroup(BaseModel):
    """Represent an operation group."""

    def __init__(
        self,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        client: "Client",
        operations: List["OperationType"],
        api_versions: List[str],
    ) -> None:
        super().__init__(yaml_data, code_model)
        self.client = client
        self.class_name: str = yaml_data["className"]
        self.property_name: str = yaml_data["propertyName"]
        self.operations = operations
        self.api_versions = api_versions

    @property
    def has_abstract_operations(self) -> bool:
        return any(o for o in self.operations if o.abstract)

    @property
    def base_class(self) -> str:
        base_classes: List[str] = []
        if self.is_mixin and self.code_model.need_mixin_abc:
            base_classes.append(f"{self.client.name}MixinABC")
        return ", ".join(base_classes)

    def imports_for_multiapi(self, async_mode: bool) -> FileImport:
        file_import = FileImport()
        relative_path = ".." if async_mode else "."
        for operation in self.operations:
            file_import.merge(
                operation.imports_for_multiapi(async_mode, relative_path=relative_path)
            )
        if (
            self.code_model.model_types or self.code_model.enums
        ) and self.code_model.options["models_mode"] == "msrest":
            file_import.add_submodule_import(
                relative_path, "models", ImportType.LOCAL, alias="_models"
            )
        return file_import

    @property
    def pylint_disable(self) -> str:
        retval: str = ""
        if self.has_abstract_operations:
            retval = add_to_pylint_disable(retval, "abstract-class-instantiated")
        if len(self.operations) > 20:
            retval = add_to_pylint_disable(retval, "too-many-public-methods")
        if len(self.class_name) > NAME_LENGTH_LIMIT:
            retval = add_to_pylint_disable(retval, "name-too-long")
        return retval

    @property
    def need_validation(self) -> bool:
        """Whether any of its operations need validation"""
        return any(o for o in self.operations if o.need_validation)

    def imports(self, async_mode: bool) -> FileImport:
        file_import = FileImport()

        relative_path = ("..." if async_mode else "..") + (
            "." if self.client.is_subclient else ""
        )
        for operation in self.operations:
            file_import.merge(
                operation.imports(async_mode, relative_path=relative_path)
            )
        # for multiapi
        if (
            (self.code_model.public_model_types)
            and self.code_model.options["models_mode"] == "msrest"
            and not self.is_mixin
        ):
            file_import.add_submodule_import(
                relative_path, "models", ImportType.LOCAL, alias="_models"
            )
        if self.code_model.need_mixin_abc:
            file_import.add_submodule_import(
                ".._vendor", f"{self.client.name}MixinABC", ImportType.LOCAL
            )
        if self.has_abstract_operations:
            file_import.add_submodule_import(
                ".._vendor", "raise_if_not_implemented", ImportType.LOCAL
            )
        if all(o.abstract for o in self.operations):
            return file_import
        file_import.add_submodule_import(
            "typing", "TypeVar", ImportType.STDLIB, TypingSection.CONDITIONAL
        )
        file_import.define_mypy_type("T", "TypeVar('T')")
        type_value = "Optional[Callable[[PipelineResponse[HttpRequest, {}HttpResponse], T, Dict[str, Any]], Any]]"
        file_import.define_mypy_type(
            "ClsType", type_value.format(""), type_value.format("Async")
        )
        return file_import

    @property
    def filename(self) -> str:
        return self.operations[0].filename

    @property
    def is_mixin(self) -> bool:
        """The operation group with no name is the direct client methods."""
        return self.property_name == ""

    @classmethod
    def from_yaml(
        cls,
        yaml_data: Dict[str, Any],
        code_model: "CodeModel",
        client: "Client",
    ) -> "OperationGroup":
        operations = [
            get_operation(o, code_model, client) for o in yaml_data["operations"]
        ]
        api_versions: OrderedSet[str] = {}
        for operation in operations:
            for api_version in operation.api_versions:
                api_versions[api_version] = None
        return cls(
            yaml_data=yaml_data,
            code_model=code_model,
            client=client,
            operations=operations,
            api_versions=list(api_versions.keys()),
        )
