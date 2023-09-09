# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from pathlib import Path
from typing import Any, Optional, Union, List
from jinja2 import PackageLoader, Environment

from .import_serializer import FileImportSerializer

from ...jsonrpc import AutorestAPI
from ..models import CodeModel, GlobalParameter
from ... import ReaderAndWriter, ReaderAndWriterAutorest

__all__ = [
    "MultiAPISerializer",
]

_FILE_TO_TEMPLATE = {
    "init": "multiapi_init.py.jinja2",
    "client": "multiapi_service_client.py.jinja2",
    "config": "multiapi_config.py.jinja2",
    "models": "multiapi_models.py.jinja2",
    "operations_mixin": "multiapi_operations_mixin.py.jinja2",
}


def _method_signature_helper(
    parameters: List[GlobalParameter], async_mode: bool
) -> List[str]:
    return [
        p.signature(async_mode)
        for p in sorted(parameters, key=lambda p: p.required, reverse=True)
    ]


def _get_file_path(filename: str, async_mode: bool) -> Path:
    filename += ".py"
    if async_mode:
        return Path("aio") / filename
    return Path(filename)


class MultiAPISerializer(ReaderAndWriter):  # pylint: disable=abstract-method
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.env = Environment(
            loader=PackageLoader("autorest.multiapi", "templates"),
            keep_trailing_newline=True,
            line_statement_prefix="##",
            line_comment_prefix="###",
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _serialize_helper(self, code_model: CodeModel, async_mode: bool) -> None:
        def _render_template(file: str, **kwargs: Any) -> str:
            template = self.env.get_template(_FILE_TO_TEMPLATE[file])
            all_params = (
                code_model.global_parameters.parameters
                + code_model.global_parameters.service_client_specific_global_parameters
            )
            positional_params = [
                p for p in all_params if p.method_location == "positional"
            ]
            keyword_only_params = [
                p for p in all_params if p.method_location == "keywordOnly"
            ]
            return template.render(
                code_model=code_model,
                async_mode=async_mode,
                positional_params=_method_signature_helper(
                    positional_params, async_mode
                ),
                keyword_only_params=_method_signature_helper(
                    keyword_only_params, async_mode
                ),
                **kwargs
            )

        # serialize init file
        self.write_file(
            _get_file_path("__init__", async_mode), _render_template("init")
        )

        # serialize service client file
        imports = FileImportSerializer(code_model.client.imports(async_mode))
        self.write_file(
            _get_file_path(code_model.client.filename, async_mode),
            _render_template("client", imports=imports),
        )

        # serialize config file
        imports = FileImportSerializer(code_model.config.imports(async_mode))
        self.write_file(
            _get_file_path("_configuration", async_mode),
            _render_template("config", imports=imports),
        )

        # serialize mixins
        if code_model.operation_mixin_group.mixin_operations:
            imports = FileImportSerializer(
                code_model.operation_mixin_group.imports(async_mode),
                code_model.operation_mixin_group.typing_definitions(async_mode),
            )
            self.write_file(
                _get_file_path("_operations_mixin", async_mode),
                _render_template("operations_mixin", imports=imports),
            )

        # serialize models
        self.write_file(Path("models.py"), _render_template("models"))

    def _serialize_version_file(self) -> None:
        if self.read_file("_version.py"):
            self.write_file("_version.py", self.read_file("_version.py"))
        elif self.read_file("version.py"):
            self.write_file("_version.py", self.read_file("version.py"))
        else:
            template = self.env.get_template("multiapi_version.py.jinja2")
            self.write_file(Path("_version.py"), template.render())

    def serialize(self, code_model: CodeModel, no_async: Optional[bool]) -> None:
        self._serialize_helper(code_model, async_mode=False)
        if not no_async:
            self._serialize_helper(code_model, async_mode=True)

        self._serialize_version_file()

        # don't erase patch file
        if self.read_file("_patch.py"):
            self.write_file("_patch.py", self.read_file("_patch.py"))

        self.write_file(Path("py.typed"), "# Marker file for PEP 561.")

        if not code_model.client.client_side_validation:
            codegen_env = Environment(
                loader=PackageLoader("autorest.codegen", "templates"),
                keep_trailing_newline=True,
                line_statement_prefix="##",
                line_comment_prefix="###",
                trim_blocks=True,
                lstrip_blocks=True,
            )
            self.write_file(
                Path("_serialization.py"),
                codegen_env.get_template("serialization.py.jinja2").render(),
            )


class MultiAPISerializerAutorest(MultiAPISerializer, ReaderAndWriterAutorest):
    def __init__(
        self, autorestapi: AutorestAPI, *, output_folder: Union[str, Path]
    ) -> None:
        super().__init__(autorestapi=autorestapi, output_folder=output_folder)
