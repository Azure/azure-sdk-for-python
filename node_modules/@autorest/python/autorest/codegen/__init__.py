# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import Dict, Any, cast
from pathlib import Path
import yaml


from .. import Plugin, PluginAutorest
from .._utils import parse_args
from .models.code_model import CodeModel
from .serializers import JinjaSerializer, JinjaSerializerAutorest
from ._utils import DEFAULT_HEADER_TEXT


def _default_pprint(package_name: str) -> str:
    return " ".join([i.capitalize() for i in package_name.split("-")])


def _validate_code_model_options(options: Dict[str, Any]) -> None:
    if options["builders_visibility"] not in ["public", "hidden", "embedded"]:
        raise ValueError(
            "The value of --builders-visibility must be either 'public', 'hidden', "
            "or 'embedded'"
        )

    if options["models_mode"] not in ["msrest", "dpg", "none"]:
        raise ValueError(
            "--models-mode can only be 'msrest', 'dpg' or 'none'. "
            "Pass in 'msrest' if you want msrest models, or "
            "'none' if you don't want any."
        )

    if not options["show_operations"] and options["builders_visibility"] == "embedded":
        raise ValueError(
            "Can not embed builders without operations. "
            "Either set --show-operations to True, or change the value of --builders-visibility "
            "to 'public' or 'hidden'."
        )

    if options["basic_setup_py"] and not options["package_version"]:
        raise ValueError("--basic-setup-py must be used with --package-version")

    if options["package_mode"] and not options["package_version"]:
        raise ValueError("--package-mode must be used with --package-version")

    if not options["show_operations"] and options["combine_operation_files"]:
        raise ValueError(
            "Can not combine operation files if you are not showing operations. "
            "If you want operation files, pass in flag --show-operations"
        )

    if options["package_mode"]:
        if (
            options["package_mode"] not in ("mgmtplane", "dataplane")
            and not Path(options["package_mode"]).exists()
        ):
            raise ValueError(
                "--package-mode can only be 'mgmtplane' or 'dataplane' or directory which contains template files"
            )

    if options["multiapi"] and options["version_tolerant"]:
        raise ValueError(
            "Can not currently generate version tolerant multiapi SDKs. "
            "We are working on creating a new multiapi SDK for version tolerant and it is not available yet."
        )

    if options["client_side_validation"] and options["version_tolerant"]:
        raise ValueError(
            "Can not generate version tolerant with --client-side-validation. "
        )

    if not (options["azure_arm"] or options["version_tolerant"]):
        _LOGGER.warning(
            "You are generating with options that would not allow the SDK to be shipped as an official Azure SDK. "
            "Please read https://aka.ms/azsdk/dpcodegen for more details."
        )


_LOGGER = logging.getLogger(__name__)


class CodeGenerator(Plugin):
    @staticmethod
    def remove_cloud_errors(yaml_data: Dict[str, Any]) -> None:
        for client in yaml_data["clients"]:
            for group in client["operationGroups"]:
                for operation in group["operations"]:
                    if not operation.get("exceptions"):
                        continue
                    i = 0
                    while i < len(operation["exceptions"]):
                        exception = operation["exceptions"][i]
                        if (
                            exception.get("schema")
                            and exception["schema"]["language"]["default"]["name"]
                            == "CloudError"
                        ):
                            del operation["exceptions"][i]
                            i -= 1
                        i += 1
        if yaml_data.get("schemas") and yaml_data["schemas"].get("objects"):
            for i in range(len(yaml_data["schemas"]["objects"])):
                obj_schema = yaml_data["schemas"]["objects"][i]
                if obj_schema["language"]["default"]["name"] == "CloudError":
                    del yaml_data["schemas"]["objects"][i]
                    break

    def _build_code_model_options(self) -> Dict[str, Any]:
        """Build en options dict from the user input while running autorest."""
        azure_arm = self.options.get("azure-arm", False)
        license_header = self.options.get("header-text", DEFAULT_HEADER_TEXT)
        if license_header:
            license_header = license_header.replace("\n", "\n# ")
            license_header = (
                "# --------------------------------------------------------------------------\n# "
                + license_header
            )
            license_header += "\n# --------------------------------------------------------------------------"

        low_level_client = cast(bool, self.options.get("low-level-client", False))
        version_tolerant = cast(bool, self.options.get("version-tolerant", True))
        show_operations = self.options.get("show-operations", not low_level_client)
        models_mode_default = (
            "none" if low_level_client or version_tolerant else "msrest"
        )
        if self.options.get("cadl_file") is not None:
            models_mode_default = "dpg"

        package_name = self.options.get("package-name")
        options: Dict[str, Any] = {
            "azure_arm": azure_arm,
            "head_as_boolean": self.options.get("head-as-boolean", True),
            "license_header": license_header,
            "keep_version_file": self.options.get("keep-version-file", False),
            "no_async": self.options.get("no-async", False),
            "no_namespace_folders": self.options.get("no-namespace-folders", False),
            "basic_setup_py": self.options.get("basic-setup-py", False),
            "package_name": package_name,
            "package_version": self.options.get("package-version"),
            "client_side_validation": self.options.get("client-side-validation", False),
            "tracing": self.options.get("tracing", show_operations),
            "multiapi": self.options.get("multiapi", False),
            "polymorphic_examples": self.options.get("polymorphic-examples", 5),
            "models_mode": self.options.get("models-mode", models_mode_default).lower(),
            "builders_visibility": self.options.get("builders-visibility"),
            "show_operations": show_operations,
            "show_send_request": self.options.get(
                "show-send-request", low_level_client or version_tolerant
            ),
            "only_path_and_body_params_positional": self.options.get(
                "only-path-and-body-params-positional",
                low_level_client or version_tolerant,
            ),
            "version_tolerant": version_tolerant,
            "low_level_client": low_level_client,
            "combine_operation_files": self.options.get(
                "combine-operation-files", version_tolerant
            ),
            "package_mode": self.options.get("package-mode"),
            "package_pprint_name": self.options.get("package-pprint-name")
            or _default_pprint(str(package_name)),
            "package_configuration": self.options.get("package-configuration"),
            "default_optional_constants_to_none": self.options.get(
                "default-optional-constants-to-none",
                low_level_client or version_tolerant,
            ),
            "generate_sample": self.options.get("generate-sample", False),
            "default_api_version": self.options.get("default-api-version"),
        }

        if options["builders_visibility"] is None:
            options["builders_visibility"] = (
                "public" if low_level_client else "embedded"
            )
        else:
            options["builders_visibility"] = options["builders_visibility"].lower()

        _validate_code_model_options(options)

        if options["models_mode"] == "none":
            # switch to falsy value for easier code writing
            options["models_mode"] = False

        # Force some options in ARM MODE:
        if azure_arm:
            options["head_as_boolean"] = True
        return options

    def get_yaml(self) -> Dict[str, Any]:
        # cadl file doesn't have to be relative to output folder
        with open(self.options["cadl_file"], "r", encoding="utf-8-sig") as fd:
            return yaml.safe_load(fd.read())

    def get_serializer(self, code_model: CodeModel):
        return JinjaSerializer(code_model, output_folder=self.output_folder)

    def process(self) -> bool:
        # List the input file, should be only one

        options = self._build_code_model_options()
        yaml_data = self.get_yaml()

        if options["azure_arm"]:
            self.remove_cloud_errors(yaml_data)

        code_model = CodeModel(yaml_data=yaml_data, options=options)
        serializer = self.get_serializer(code_model)
        serializer.serialize()

        return True


class CodeGeneratorAutorest(CodeGenerator, PluginAutorest):
    def get_options(self) -> Dict[str, Any]:
        if self._autorestapi.get_boolean_value("python3-only") is False:
            _LOGGER.warning(
                "You have passed in --python3-only=False. We have force overriden "
                "this to True."
            )
        if self._autorestapi.get_boolean_value("add-python3-operation-files"):
            _LOGGER.warning(
                "You have passed in --add-python3-operation-files. "
                "This flag no longer has an effect bc all SDKs are now Python3 only."
            )
        if self._autorestapi.get_boolean_value("reformat-next-link"):
            _LOGGER.warning(
                "You have passed in --reformat-next-link. We have force overriden "
                "this to False because we no longer reformat initial query parameters into next "
                "calls unless explicitly defined in the service definition."
            )
        options = {
            "azure-arm": self._autorestapi.get_boolean_value("azure-arm"),
            "header-text": self._autorestapi.get_value("header-text"),
            "low-level-client": self._autorestapi.get_boolean_value(
                "low-level-client", False
            ),
            "version-tolerant": self._autorestapi.get_boolean_value(
                "version-tolerant", True
            ),
            "show-operations": self._autorestapi.get_boolean_value("show-operations"),
            "python3-only": self._autorestapi.get_boolean_value("python3-only"),
            "head-as-boolean": self._autorestapi.get_boolean_value(
                "head-as-boolean", False
            ),
            "keep-version-file": self._autorestapi.get_boolean_value(
                "keep-version-file"
            ),
            "no-async": self._autorestapi.get_boolean_value("no-async"),
            "no-namespace-folders": self._autorestapi.get_boolean_value(
                "no-namespace-folders"
            ),
            "basic-setup-py": self._autorestapi.get_boolean_value("basic-setup-py"),
            "package-name": self._autorestapi.get_value("package-name"),
            "package-version": self._autorestapi.get_value("package-version"),
            "client-side-validation": self._autorestapi.get_boolean_value(
                "client-side-validation"
            ),
            "tracing": self._autorestapi.get_boolean_value("trace"),
            "multiapi": self._autorestapi.get_boolean_value("multiapi", False),
            "polymorphic-examples": self._autorestapi.get_value("polymorphic-examples"),
            "models-mode": self._autorestapi.get_value("models-mode"),
            "builders-visibility": self._autorestapi.get_value("builders-visibility"),
            "show-send-request": self._autorestapi.get_boolean_value(
                "show-send-request"
            ),
            "only-path-and-body-params-positional": self._autorestapi.get_boolean_value(
                "only-path-and-body-params-positional"
            ),
            "combine-operation-files": self._autorestapi.get_boolean_value(
                "combine-operation-files"
            ),
            "package-mode": self._autorestapi.get_value("package-mode"),
            "package-pprint-name": self._autorestapi.get_value("package-pprint-name"),
            "package-configuration": self._autorestapi.get_value(
                "package-configuration"
            ),
            "default-optional-constants-to-none": self._autorestapi.get_boolean_value(
                "default-optional-constants-to-none"
            ),
            "generate-sample": self._autorestapi.get_boolean_value("generate-sample"),
            "default-api-version": self._autorestapi.get_value("default-api-version"),
        }
        return {k: v for k, v in options.items() if v is not None}

    def get_yaml(self) -> Dict[str, Any]:
        inputs = self._autorestapi.list_inputs()
        _LOGGER.debug("Possible Inputs: %s", inputs)
        if "code-model-v4-no-tags.yaml" not in inputs:
            raise ValueError("code-model-v4-no-tags.yaml must be a possible input")

        if self._autorestapi.get_value("input-yaml"):
            input_yaml = self._autorestapi.get_value("input-yaml")
            file_content = self._autorestapi.read_file(input_yaml)
        else:
            inputs = self._autorestapi.list_inputs()
            _LOGGER.debug("Possible Inputs: %s", inputs)
            if "code-model-v4-no-tags.yaml" not in inputs:
                raise ValueError("code-model-v4-no-tags.yaml must be a possible input")

            file_content = self._autorestapi.read_file("code-model-v4-no-tags.yaml")

        # Parse the received YAML
        return yaml.safe_load(file_content)

    def get_serializer(self, code_model: CodeModel):
        return JinjaSerializerAutorest(
            self._autorestapi,
            code_model,
            output_folder=self.output_folder,
        )


if __name__ == "__main__":
    # CADL pipeline will call this
    args, unknown_args = parse_args()
    CodeGenerator(
        output_folder=args.output_folder, cadl_file=args.cadl_file, **unknown_args
    ).process()
