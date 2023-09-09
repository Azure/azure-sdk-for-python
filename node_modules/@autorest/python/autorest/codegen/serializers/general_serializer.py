# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, List
from jinja2 import Environment
from .import_serializer import FileImportSerializer, TypingSection
from ..models.imports import MsrestImportType
from ..models import (
    FileImport,
    ImportType,
    CodeModel,
    TokenCredentialType,
    Client,
)
from .client_serializer import ClientSerializer, ConfigSerializer

_PACKAGE_MODE_FILES = [
    "CHANGELOG.md.jinja2",
    "dev_requirements.txt.jinja2",
    "LICENSE.jinja2",
    "MANIFEST.in.jinja2",
    "README.md.jinja2",
]


class GeneralSerializer:
    """General serializer for SDK root level files"""

    def __init__(self, code_model: CodeModel, env: Environment, async_mode: bool):
        self.code_model = code_model
        self.env = env
        self.async_mode = async_mode

    def serialize_setup_file(self) -> str:
        template = self.env.get_template("packaging_templates/setup.py.jinja2")
        params = {}
        params.update(self.code_model.options)
        return template.render(code_model=self.code_model, **params)

    def serialize_package_file(self, template_name: str, **kwargs: Any) -> str:
        template = self.env.get_template(template_name)
        package_parts = (self.code_model.options["package_name"] or "").split("-")[:-1]
        token_credential = any(
            c
            for c in self.code_model.clients
            if isinstance(getattr(c.credential, "type", None), TokenCredentialType)
        )
        version = self.code_model.options["package_version"]
        if any(x in version for x in ["a", "b", "rc"]) or version[0] == "0":
            dev_status = "4 - Beta"
        else:
            dev_status = "5 - Production/Stable"
        params = {
            "code_model": self.code_model,
            "dev_status": dev_status,
            "token_credential": token_credential,
            "pkgutil_names": [
                ".".join(package_parts[: i + 1]) for i in range(len(package_parts))
            ],
            "init_names": [
                "/".join(package_parts[: i + 1]) + "/__init__.py"
                for i in range(len(package_parts))
            ],
            "client_name": self.code_model.clients[0].name,
            "namespace": self.code_model.namespace,
        }
        params.update(self.code_model.options)
        params.update(kwargs)
        return template.render(**params)

    def serialize_pkgutil_init_file(self) -> str:
        template = self.env.get_template("pkgutil_init.py.jinja2")
        return template.render()

    def serialize_init_file(self, clients: List[Client]) -> str:
        template = self.env.get_template("init.py.jinja2")
        return template.render(
            code_model=self.code_model,
            clients=clients,
            async_mode=self.async_mode,
        )

    def serialize_service_client_file(self, clients: List[Client]) -> str:
        template = self.env.get_template("client_container.py.jinja2")

        imports = FileImport()
        for client in clients:
            imports.merge(client.imports(self.async_mode))

        return template.render(
            code_model=self.code_model,
            clients=clients,
            async_mode=self.async_mode,
            get_serializer=ClientSerializer,
            imports=FileImportSerializer(imports),
        )

    def serialize_vendor_file(self, clients: List[Client]) -> str:
        template = self.env.get_template("vendor.py.jinja2")

        # configure imports
        file_import = FileImport()
        if self.code_model.need_request_converter:
            file_import.add_submodule_import(
                "azure.core.pipeline.transport",
                "HttpRequest",
                ImportType.AZURECORE,
            )

        if self.code_model.need_mixin_abc:
            file_import.add_submodule_import(
                "abc",
                "ABC",
                ImportType.STDLIB,
            )
            file_import.add_submodule_import(
                "azure.core",
                f"{'Async' if self.async_mode else ''}PipelineClient",
                ImportType.AZURECORE,
                TypingSection.TYPING,
            )
            file_import.add_msrest_import(
                self.code_model,
                ".." if self.async_mode else ".",
                MsrestImportType.SerializerDeserializer,
                TypingSection.TYPING,
            )
            for client in clients:
                file_import.add_submodule_import(
                    "._configuration",
                    f"{client.name}Configuration",
                    ImportType.LOCAL,
                )
        if self.code_model.has_etag:
            file_import.add_submodule_import("typing", "Optional", ImportType.STDLIB)
            file_import.add_submodule_import(
                "azure.core",
                "MatchConditions",
                ImportType.AZURECORE,
            )

        return template.render(
            code_model=self.code_model,
            imports=FileImportSerializer(
                file_import,
            ),
            async_mode=self.async_mode,
            clients=clients,
        )

    def serialize_config_file(self, clients: List[Client]) -> str:
        template = self.env.get_template("config_container.py.jinja2")
        imports = FileImport()
        for client in self.code_model.clients:
            imports.merge(client.config.imports(self.async_mode))
        return template.render(
            code_model=self.code_model,
            async_mode=self.async_mode,
            imports=FileImportSerializer(imports),
            get_serializer=ConfigSerializer,
            clients=clients,
        )

    def serialize_version_file(self) -> str:
        template = self.env.get_template("version.py.jinja2")
        return template.render(code_model=self.code_model)

    def serialize_serialization_file(self) -> str:
        template = self.env.get_template("serialization.py.jinja2")
        return template.render(code_model=self.code_model)

    def serialize_model_base_file(self) -> str:
        template = self.env.get_template("model_base.py.jinja2")
        return template.render(code_model=self.code_model)

    def serialize_validation_file(self) -> str:
        template = self.env.get_template("validation.py.jinja2")
        return template.render(code_model=self.code_model)
