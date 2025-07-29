import os
import json
import tempfile
import unittest
from pathlib import Path

import pytest
from packaging_tools.generate_utils import update_servicemetadata


"""
Create metadata file

Update metadata file

Update MANIFEST.IN

No need to update MANIFEST.IN
"""

MANIFEST_TEMP = """recursive-include tests *.py *.yaml
include *.md
include azure/__init__.py
include azure/mgmt/__init__.py
"""


class TestServiceMetadata(unittest.TestCase):
    def setUp(self):
        self.sdk_folder = "sdk"
        self.data = {
            "specFolder": "../azure-rest-api-specs",
            "headSha": "e295fe97eee3709668d3e5f7f8b434026b814ef9",
            "headRef": "master",
            "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
        }
        self.config = {
            "meta": {
                "autorest_options": {
                    "version": "3.0.6369",
                    "use": "@autorest/python@5.4.3",
                    "python": "",
                    "python-mode": "update",
                    "sdkrel:python-sdks-folder": "./sdk/.",
                    "multiapi": "",
                    "track2": "",
                },
                "advanced_options": {
                    "create_sdk_pull_requests": True,
                    "sdk_generation_pull_request_base": "integration_branch",
                },
                "repotag": "azure-sdk-for-python-track2",
                "version": "0.2.0",
            },
            "projects": {"./azure-rest-api-specs/specification/operationalinsights/resource-manager/readme.md": {}},
        }
        self.folder_name = "monitor"
        self.package_name = "azure-mgmt-monitor"
        self.spec_folder = "./"
        self.input_readme = "azure-rest-api-specs/specification/operationalinsights/resource-manager/readme.md"

    def test_metadata(self):

        with tempfile.TemporaryDirectory() as temp_dir:
            # Init directories
            self.sdk_folder = str(Path(temp_dir, "sdk"))
            self.spec_folder = str(Path(temp_dir, "spec"))
            os.makedirs(self.sdk_folder)
            os.makedirs(self.spec_folder)

            readme_file = str(Path(self.spec_folder, self.input_readme))
            self.config["projects"][readme_file] = {}

            package_folder = Path(self.sdk_folder, self.folder_name, self.package_name).expanduser()
            metadata_file_path = os.path.join(package_folder, "_metadata.json")
            manifest_file = os.path.join(package_folder, "MANIFEST.in")
            os.makedirs(package_folder)

            # Test MANIFEST.in does not exist
            update_servicemetadata(
                sdk_folder=self.sdk_folder,
                data=self.data,
                config=self.config,
                folder_name=self.folder_name,
                package_name=self.package_name,
                spec_folder=self.spec_folder,
                input_readme=self.input_readme,
            )

            assert os.path.isfile(metadata_file_path) == True
            # Do not create MANIFEST.in, if it does not exist
            assert os.path.isfile(manifest_file) == False

            # Test update metadata
            with open(metadata_file_path, "w") as f:
                json.dump({"autorest": "3.0.0"}, f, indent=2)
            update_servicemetadata(
                sdk_folder=self.sdk_folder,
                data=self.data,
                config=self.config,
                folder_name=self.folder_name,
                package_name=self.package_name,
                spec_folder=self.spec_folder,
                input_readme=self.input_readme,
            )

            assert os.path.isfile(metadata_file_path) == True
            assert os.path.isfile(manifest_file) == False
            with open(metadata_file_path, "r") as f:
                md = json.load(f)
                assert md["autorest"] == "3.0.6369"

            # Test update MANIFEST.in
            with open(manifest_file, "w") as f:
                f.write(MANIFEST_TEMP)
            update_servicemetadata(
                sdk_folder=self.sdk_folder,
                data=self.data,
                config=self.config,
                folder_name=self.folder_name,
                package_name=self.package_name,
                spec_folder=self.spec_folder,
                input_readme=self.input_readme,
            )

            assert os.path.isfile(metadata_file_path) == True
            assert os.path.isfile(manifest_file) == True

            # Test update MANIFEST.in again
            update_servicemetadata(
                sdk_folder=self.sdk_folder,
                data=self.data,
                config=self.config,
                folder_name=self.folder_name,
                package_name=self.package_name,
                spec_folder=self.spec_folder,
                input_readme=self.input_readme,
            )

            assert os.path.isfile(metadata_file_path) == True
            assert os.path.isfile(manifest_file) == True
