import os

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages


repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sdk_root = os.path.join(repo_root, "sdk")
core_service_root = os.path.join(sdk_root, "core")
storage_service_root = os.path.join(sdk_root, "storage")


def test_discovery():
    results = discover_targeted_packages("azure*", core_service_root)

    # if in a set, this should be empty
    non_empty_results = discover_targeted_packages("azure-core", core_service_root)

    assert len(results) > 1
    assert len(non_empty_results) == 1


def test_discovery_against_sdk():
    package_directories = discover_targeted_packages("**", sdk_root)

    # ensure we didn't accidentally pick up a couple known packages from within a tests directory

    known_mgmt_test_setup = os.path.join(sdk_root, "netapp", "azure-mgmt-netapp", "tests", "setup.py")
    known_test_core_setup = os.path.join(
        repo_root, "sdk", "core", "azure-core", "tests", "testserver_tests", "coretestserver", "setup.py"
    )

    assert known_test_core_setup not in package_directories
    assert known_mgmt_test_setup not in package_directories

    # this is effectively checking to ensure we don't crash on any of the packages
    assert len(package_directories) > 0


def test_discovery_omit_mgmt():
    results = discover_targeted_packages("azure*", storage_service_root, filter_type="Omit_management")

    assert [os.path.basename(result) for result in results] == [
        "azure-storage-blob",
        "azure-storage-blob-changefeed",
        "azure-storage-extensions",
        "azure-storage-file-datalake",
        "azure-storage-file-share",
        "azure-storage-queue",
    ]


def test_discovery_omit_build():
    results = discover_targeted_packages("*", core_service_root, filter_type="Build")

    assert [os.path.basename(result) for result in results] == [
        "azure-core",
        "azure-core-experimental",
        "azure-core-tracing-opentelemetry",
        "azure-mgmt-core",
        "corehttp",
    ]


def test_discovery_single_package():
    results = discover_targeted_packages("azure-core", core_service_root, filter_type="Build")

    assert [os.path.basename(result) for result in results] == [
        "azure-core",
    ]


def test_discovery_omit_regression():
    results = discover_targeted_packages("*", core_service_root, filter_type="Regression")

    assert [os.path.basename(result) for result in results] == [
        "azure-core",
        "azure-core-experimental",
        "azure-core-tracing-opentelemetry",
        "corehttp",
    ]

    storage_results = discover_targeted_packages("azure*", storage_service_root, filter_type="Regression")

    assert [os.path.basename(result) for result in storage_results] == [
        "azure-storage-blob",
        "azure-storage-blob-changefeed",
        "azure-storage-extensions",
        "azure-storage-file-datalake",
        "azure-storage-file-share",
        "azure-storage-queue",
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
        "azure-core-tracing-opentelemetry",
        "azure-mgmt-core",
    ]
