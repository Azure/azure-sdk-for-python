import tempfile
import os

from tempfile import TemporaryDirectory
from unittest.mock import patch

from typing import List

from ci_tools.functions import find_whl


def create_temp_directory(fake_creation_paths: List[str]) -> TemporaryDirectory:
    tmp_dir = TemporaryDirectory()

    for file in fake_creation_paths:
        target_path = os.path.join(tmp_dir.name, file)
        dirname = os.path.join(tmp_dir.name, os.path.dirname(file))

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        with open(target_path, "w"):
            pass

    return tmp_dir


def create_basic_temp_dir() -> TemporaryDirectory:
    tmp_dir = create_temp_directory(
        [
            os.path.join("azure-common", "azure_common-1.1.29-py3-none-any.whl"),
            os.path.join("azure-core", "azure_core-1.26.5-py3-none-any.whl"),
            os.path.join("azure-core-experimental", "azure_core_experimental-1.0.0b3-py3-none-any.whl"),
            os.path.join("azure-tracing-opencensus", "azure_core_tracing_opencensus-1.0.0b9-py3-none-any.whl"),
            os.path.join(
                "azure-core-tracing-opentelemetry", "azure_core_tracing_opentelemetry-1.0.0b10-py3-none-any.whl"
            ),
            os.path.join("azure-mgmt-core", "azure_mgmt_core-1.4.0-py3-none-any.whl"),
            os.path.join(
                "azure-servicemanagement-legacy", "azure_servicemanagement_legacy-0.20.7-py2.py3-none-any.whl"
            ),
        ]
    )
    return tmp_dir


@patch("ci_tools.functions.get_interpreter_compatible_tags")
def test_find_discovers_standard_whls(test_patch):
    tmp_dir = create_basic_temp_dir()
    test_patch.return_value = ["py3-none-any"]

    # basic positive cases
    found_core = find_whl(tmp_dir.name, "azure-core", "1.26.5")
    found_legacy = find_whl(tmp_dir.name, "azure-servicemanagement-legacy", "0.20.7")
    assert found_core is not None
    assert found_legacy is not None

    # basic negative cases
    not_found_core = find_whl(tmp_dir.name, "azure-core", "1.26.4")
    assert not_found_core is None

    tmp_dir.cleanup()


@patch("ci_tools.functions.get_interpreter_compatible_tags")
def test_find_whl_fails_on_incompatible_interpreter(test_patch):
    tmp_dir = create_basic_temp_dir()
    test_patch.return_value = []

    found = find_whl(tmp_dir.name, "azure-core", "1.26.5")
    assert found is None

    tmp_dir.cleanup()
