# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from jinja2 import Environment
from .import_serializer import FileImportSerializer
from ..models import CodeModel, FileImport, ImportType


class PatchSerializer:
    def __init__(self, env: Environment, code_model: CodeModel) -> None:
        self.env = env
        self.code_model = code_model

    def serialize(self) -> str:
        template = self.env.get_template("patch.py.jinja2")
        imports = FileImport()
        imports.add_submodule_import("typing", "List", ImportType.STDLIB)
        return template.render(
            code_model=self.code_model,
            imports=FileImportSerializer(imports),
        )
