import os, shutil

from typing import List
from ci_tools.scenario.generation import replace_dev_reqs
from ci_tools.parsing import ParsedSetup

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
sample_dev_reqs_folder = os.path.join(integration_folder, "scenarios", "dev_requirement_samples")
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
core_location = os.path.join(repo_root, "sdk", "core", "azure-core")


def create_temporary_scenario(tmp_directory_create, target_file: str) -> str:
    """
    Creates a temporary directory, copies a target scenario file to it, and returns the path to that copied file.
    """
    tmp_dir = tmp_directory_create([])

    if not os.path.exists(target_file):
        raise Exception("Unable to create a temporary scenario based on a nonexistent requirements file.")

    if not os.path.isfile(target_file):
        raise Exception("Unable to create a temporary scenario based on a target that is not actually a file.")

    filename = os.path.basename(target_file)
    move_target = os.path.join(tmp_dir, filename)

    shutil.copy(target_file, move_target)

    return move_target


def get_requirements_from_file(requirements_file: str) -> List[str]:
    with open(requirements_file, "r", encoding="utf-8") as f:
        results = f.readlines()

    return [line.strip() for line in results if line.strip()]


def test_replace_dev_reqs_specifiers(tmp_directory_create):
    """
    Specifiers should always be pointed at an external source, nothing to build locally. Nontheless we need to confirm
    that we don't accidentally trip the replacement logic.
    """
    target_file = os.path.join(sample_dev_reqs_folder, "specifiers_requirements.txt")
    requirements_file = create_temporary_scenario(tmp_directory_create, target_file)

    requirements_before = get_requirements_from_file(requirements_file)
    replace_dev_reqs(requirements_file, core_location, None)
    requirements_after = get_requirements_from_file(requirements_file)

    assert requirements_before == requirements_after


def test_replace_dev_reqs_relative(tmp_directory_create):
    """
    This test exercises the primary workload for replace_dev_reqs, as all local relative requirements must be
    prebuilt in CI to avoid parallel access issues while pip is attempting to assemble a wheel.
    """
    target_file = os.path.join(sample_dev_reqs_folder, "relative_requirements.txt")
    requirements_file = create_temporary_scenario(tmp_directory_create, target_file)
    expected_output_folder = os.path.join(repo_root, "sdk", "core", "azure-core", ".tmp_whl_dir")

    # Get the current relative versions of the packages to properly construct the expected results
    coretestserver_version = ParsedSetup.from_path(
        os.path.join(repo_root, "sdk", "core", "azure-core", "tests", "testserver_tests", "coretestserver")
    ).version
    identity_version = ParsedSetup.from_path(os.path.join(repo_root, "sdk", "identity", "azure-identity")).version
    mgmt_core_version = ParsedSetup.from_path(os.path.join(repo_root, "sdk", "core", "azure-mgmt-core")).version
    sdk_tools_version = ParsedSetup.from_path(os.path.join(repo_root, "tools", "azure-sdk-tools")).version
    core_version = ParsedSetup.from_path(os.path.join(repo_root, "sdk", "core", "azure-core")).version

    expected_results = [
        os.path.join(expected_output_folder, f"coretestserver-{coretestserver_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"coretestserver-{coretestserver_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_identity-{identity_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_identity-{identity_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_mgmt_core-{mgmt_core_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_mgmt_core-{mgmt_core_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_sdk_tools-{sdk_tools_version}-py3-none-any.whl[build]"),
        os.path.join(expected_output_folder, f"azure_sdk_tools-{sdk_tools_version}-py3-none-any.whl[build]"),
        os.path.join(expected_output_folder, f"azure_core-{core_version}-py3-none-any.whl"),
        os.path.join(expected_output_folder, f"azure_core-{core_version}-py3-none-any.whl"),
    ]
    requirements_before = get_requirements_from_file(requirements_file)
    replace_dev_reqs(requirements_file, core_location, None)
    requirements_after = get_requirements_from_file(requirements_file)

    assert requirements_before != requirements_after
    assert requirements_after == expected_results


def test_replace_dev_reqs_remote(tmp_directory_create):
    """
    "Remote" reqs are requirements that are reached out via some combination of VCS or HTTP. This includes
        git+https:// for version controlled source that will build in its own silo.
        https:// for raw wheels

    This test is similar to test_replace_dev_reqs_specifiers in that we're expecting proper no-ops.
    """
    target_file = os.path.join(sample_dev_reqs_folder, "remote_requirements.txt")
    requirements_file = create_temporary_scenario(tmp_directory_create, target_file)

    requirements_before = get_requirements_from_file(requirements_file)
    replace_dev_reqs(requirements_file, core_location, None)
    requirements_after = get_requirements_from_file(requirements_file)
    assert requirements_before == requirements_after
