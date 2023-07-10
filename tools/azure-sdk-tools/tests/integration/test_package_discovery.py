import os

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages


repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
core_service_root = os.path.join(repo_root, "sdk", "core")
storage_service_root = os.path.join(repo_root, "sdk", "storage")


def test_toml_result():
    package_with_toml = os.path.join(core_service_root, "azure-core")

    parsed_setup = ParsedSetup.from_path(package_with_toml)
    result = parsed_setup.get_build_config()

    expected = {
        "type_check_samples": False,
        "verifytypes": False,
        "pyright": False,
    }

    assert expected == result


def test_discovery():
    results = discover_targeted_packages("azure*", core_service_root)

    # if in a set, this should be empty
    non_empty_results = discover_targeted_packages("azure-servicemanagement-legacy", core_service_root)

    assert len(results) > 1
    assert len(non_empty_results) == 1


def test_discovery_omit_mgmt():
    results = discover_targeted_packages("azure*", storage_service_root, filter_type="Omit_management")

    assert [os.path.basename(result) for result in results] == [
        "azure-storage-blob",
        "azure-storage-blob-changefeed",
        "azure-storage-file-datalake",
        "azure-storage-file-share",
        "azure-storage-queue"
    ]

def test_discovery_omit_build():
    results = discover_targeted_packages("azure*", core_service_root, filter_type="Build")

    assert [os.path.basename(result) for result in results] == [
        "azure-core",
        "azure-core-experimental",
        "azure-core-tracing-opencensus",
        "azure-core-tracing-opentelemetry",
        "azure-mgmt-core",
    ]

def test_discovery_single_package():
    results = discover_targeted_packages("azure-servicemanagement-legacy", core_service_root, filter_type="Build")

    assert [os.path.basename(result) for result in results] == [
        "azure-servicemanagement-legacy",
    ]

def test_discovery_omit_regression():
    results = discover_targeted_packages("azure*", core_service_root, filter_type="Regression")

    assert [os.path.basename(result) for result in results] == [
        "azure-core",
        "azure-core-experimental",
        "azure-core-tracing-opencensus",
        "azure-core-tracing-opentelemetry"
    ]

    storage_results = discover_targeted_packages("azure*", storage_service_root, filter_type="Regression")

    assert [os.path.basename(result) for result in storage_results] == [
        "azure-storage-blob",
        "azure-storage-blob-changefeed",
        "azure-storage-file-datalake",
        "azure-storage-file-share",
        "azure-storage-queue"
    ]


def test_discovery_honors_contains_filter():
    
    storage_results = discover_targeted_packages("azure*", storage_service_root, "file", filter_type="Regression")

    assert [os.path.basename(result) for result in storage_results] == [
        "azure-storage-file-datalake",
        "azure-storage-file-share",
    ]



def test_discovery_honors_override():
    os.environ["ENABLE_AZURE_COMMON"] = "true"
    os.environ["ENABLE_AZURE_SERVICEMANAGEMENT_LEGACY"] = "false"

    results = discover_targeted_packages("azure*", core_service_root)

    assert [os.path.basename(result) for result in results] == [
        "azure-common",
        "azure-core",
        "azure-core-experimental",
        "azure-core-tracing-opencensus",
        "azure-core-tracing-opentelemetry",
        "azure-mgmt-core",
    ]
    