# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import logging
import json

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, cast, Any

from .serializers import MultiAPISerializer, MultiAPISerializerAutorest
from .models import CodeModel
from .utils import _get_default_api_version_from_list

from .. import Plugin, PluginAutorest, ReaderAndWriter, ReaderAndWriterAutorest

_LOGGER = logging.getLogger(__name__)


class MultiApiScriptPlugin(Plugin):  # pylint: disable=abstract-method
    def process(self) -> bool:
        return self.generator.process()

    @property
    def generator(self) -> "MultiAPI":
        return MultiAPI(
            input_package_name=self.options.get("package-name"),
            output_folder=self.options["output-folder"],
            user_specified_default_api=self.options.get("default-api"),
            no_async=self.options.get("no-async", False),
        )


class MultiApiScriptPluginAutorest(MultiApiScriptPlugin, PluginAutorest):
    @property
    def generator(self) -> "MultiAPI":
        return MultiAPIAutorest(
            autorestapi=self._autorestapi,
            input_package_name=self.options.get("package-name"),
            output_folder=self.output_folder,
            user_specified_default_api=self.options.get("default-api"),
            no_async=self.options.get("no-async", False),
        )

    def get_options(self) -> Dict[str, Any]:
        options = {
            "package-name": self._autorestapi.get_value("package-name"),
            "default-api": self._autorestapi.get_value("default-api"),
            "no-async": self._autorestapi.get_value("no-async"),
        }
        return {k: v for k, v in options.items() if v is not None}


class MultiAPI(ReaderAndWriter):  # pylint: disable=abstract-method
    def __init__(
        self,
        *,
        input_package_name: Optional[str] = None,
        output_folder: str,
        no_async: Optional[bool] = False,
        user_specified_default_api: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(output_folder=Path(output_folder).resolve(), **kwargs)
        if input_package_name is None:
            raise ValueError(
                "package-name is required, either provide it as args or check your readme configuration"
            )
        self.input_package_name = input_package_name
        _LOGGER.debug("Received package name %s", input_package_name)
        _LOGGER.debug("Received output-folder %s", output_folder)
        self.output_package_name: str = ""
        self.no_async = no_async
        self.user_specified_default_api = user_specified_default_api

    @property
    def default_api_version(self) -> str:
        return _get_default_api_version_from_list(
            self.mod_to_api_version,
            [p.name for p in self.paths_to_versions],
            self.preview_mode,
            self.user_specified_default_api,
        )

    @property
    def default_version_metadata(self) -> Dict[str, Any]:
        # get client name from default api version
        path_to_default_version = Path()
        for path_to_version in self.paths_to_versions:
            if self.default_api_version.replace("-", "_") == path_to_version.stem:
                path_to_default_version = path_to_version
                break
        return json.loads(self.read_file(path_to_default_version / "_metadata.json"))

    @property
    def module_name(self) -> str:
        """From a syntax like package_name#submodule, build a package name
        and complete module name.
        """
        split_package_name = self.input_package_name.split("#")
        package_name = split_package_name[0]
        module_name = package_name.replace("-", ".")
        if len(split_package_name) >= 2:
            module_name = ".".join([module_name, split_package_name[1]])
            self.output_package_name = package_name
        else:
            self.output_package_name = self.input_package_name
        return module_name

    @property
    def preview_mode(self) -> bool:
        # If True, means the auto-profile will consider preview versions.
        # If not, if it exists a stable API version for a global or RT, will always be used
        return cast(
            bool,
            self.user_specified_default_api
            and "preview" in self.user_specified_default_api,
        )

    @property
    def paths_to_versions(self) -> List[Path]:
        paths_to_versions = []
        directory = [x for x in self.output_folder.iterdir() if x.is_dir()]
        directory.sort()
        for child in directory:
            child_dir = (self.output_folder / child).resolve()
            if Path(child_dir / "_metadata.json") in child_dir.iterdir():
                paths_to_versions.append(Path(child.stem))
        return paths_to_versions

    @property
    def version_path_to_metadata(self) -> Dict[Path, Dict[str, Any]]:
        return {
            version_path: json.loads(self.read_file(version_path / "_metadata.json"))
            for version_path in self.paths_to_versions
        }

    @property
    def mod_to_api_version(self) -> Dict[str, str]:
        mod_to_api_version: Dict[str, str] = defaultdict(str)
        for version_path in self.paths_to_versions:
            metadata_json = json.loads(self.read_file(version_path / "_metadata.json"))
            version = metadata_json["chosen_version"]
            total_api_version_list = metadata_json["total_api_version_list"]
            if not version:
                if total_api_version_list:
                    sys.exit(
                        f"Unable to match {total_api_version_list} to label {version_path.stem}"
                    )
                else:
                    sys.exit(f"Unable to extract api version of {version_path.stem}")
            mod_to_api_version[version_path.name] = version
        return mod_to_api_version

    @property
    def serializer(self) -> MultiAPISerializer:
        return MultiAPISerializer()

    def process(self) -> bool:
        _LOGGER.info("Generating multiapi client")

        code_model = CodeModel(
            module_name=self.module_name,
            package_name=self.output_package_name,
            default_api_version=self.default_api_version,
            preview_mode=self.preview_mode,
            default_version_metadata=self.default_version_metadata,
            mod_to_api_version=self.mod_to_api_version,
            version_path_to_metadata=self.version_path_to_metadata,
            user_specified_default_api=self.user_specified_default_api,
        )

        multiapi_serializer = self.serializer
        multiapi_serializer.serialize(code_model, self.no_async)

        _LOGGER.info("Done!")
        return True


class MultiAPIAutorest(MultiAPI, ReaderAndWriterAutorest):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @property
    def serializer(self) -> MultiAPISerializer:
        return MultiAPISerializerAutorest(
            self._autorestapi, output_folder=self.output_folder
        )
