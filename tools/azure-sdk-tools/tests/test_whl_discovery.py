import os

from unittest.mock import patch

from tempfile import TemporaryDirectory

from ci_tools.functions import find_whl, find_sdist


integration_folder = os.path.join(os.path.dirname(__file__), "integration")
tags_folder = os.path.join(integration_folder, "scenarios", "sample_interpreter_tags")


def create_basic_temp_dir(tmp_directory_create) -> str:
    tmp_dir = tmp_directory_create(
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
def test_find_discovers_standard_whls(test_patch, tmp_directory_create):
    tmp_dir = create_basic_temp_dir(tmp_directory_create)
    test_patch.return_value = ["py3-none-any"]

    # basic positive cases
    found_core = find_whl(tmp_dir, "azure-core", "1.26.5")
    found_legacy = find_whl(tmp_dir, "azure-servicemanagement-legacy", "0.20.7")
    assert found_core is not None
    assert found_legacy is not None

    # basic negative cases
    not_found_core = find_whl(tmp_dir, "azure-core", "1.26.4")
    assert not_found_core is None


@patch("ci_tools.functions.get_interpreter_compatible_tags")
def test_find_whl_fails_on_incompatible_interpreter(test_patch, tmp_directory_create):
    tmp_dir = create_basic_temp_dir(tmp_directory_create)
    test_patch.return_value = []

    found = find_whl(tmp_dir, "azure-core", "1.26.5")
    assert found is None


@patch("ci_tools.functions.get_interpreter_compatible_tags")
def test_find_whl_discovers_specific_wheels(test_patch, tmp_directory_create):
    tmp_dir = tmp_directory_create(
        [
            "azure_storage_extensions-1.0.0b1-cp310-cp310-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-linux_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-macosx_11_0_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-win32.whl",
            "azure-storage-extensions-1.0.0b1.tar.gz",
        ]
    )

    with open(os.path.join(tags_folder, "from_WSL_310.txt"), "r", encoding="utf-8") as f:
        compatible_tags = [line.strip() for line in f.readlines()]

    test_patch.return_value = compatible_tags
    found = find_whl(tmp_dir, "azure-storage-extensions", "1.0.0b1")
    assert isinstance(found, str)


@patch("ci_tools.functions.get_interpreter_compatible_tags")
def test_find_sdist_discovers_specific_sdist(test_patch, tmp_directory_create):
    tmp_dir = tmp_directory_create(
        [
            "azure_storage_extensions-1.0.0b1-cp310-cp310-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp310-cp310-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp311-cp311-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp312-cp312-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp37-cp37m-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp38-cp38-win32.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-linux_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-macosx_10_9_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-macosx_11_0_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-win_amd64.whl",
            "azure_storage_extensions-1.0.0b1-cp39-cp39-win32.whl",
            "azure-storage-extensions-1.0.0b1.tar.gz",
        ]
    )

    with open(os.path.join(tags_folder, "from_WSL_310.txt"), "r", encoding="utf-8") as f:
        compatible_tags = [line.strip() for line in f.readlines()]

    test_patch.return_value = compatible_tags
    found = find_sdist(tmp_dir, "azure-storage-extensions", "1.0.0b1")
    assert isinstance(found, str)
