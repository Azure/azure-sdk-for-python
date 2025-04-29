import re
import subprocess
import pytest
import os
import difflib

from azure.projects._bicep.utils import generate_suffix

SUPPRESS_WARNINGS = ["no-unused-params", "no-unused-existing-resources"]
SUPPRESS_ERRORS = ["BCP104"]


def _get_infra_dir() -> str:
    test_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(test_dir, "test_infra")


def _compare_outputs(output_dir, ref_dir, test_dir):
    for _, _, files in os.walk(os.path.join(output_dir, ref_dir)):
        for filename in files:
            with open(os.path.join(output_dir, ref_dir, filename), "r") as _ref:
                ref_file = _ref.readlines()
            with open(os.path.join(output_dir, test_dir, filename), "r") as _test:
                test_file = _test.readlines()
            diff = difflib.unified_diff(
                ref_file,
                test_file,
                fromfile=f"{ref_dir}/{filename}",
                tofile=f"{test_dir}/{filename}",
            )
            changes = "".join(diff)
            has_changes = bool(changes)
            assert not has_changes, "\n" + changes
            os.remove(os.path.join(output_dir, test_dir, filename))
    os.rmdir(os.path.join(output_dir, test_dir))


@pytest.fixture
def _compare_exports(request):
    output_dir = _get_infra_dir()
    ref_dir = request.node.name
    test_dir = f"infra_{request.node.name}_{generate_suffix()}"
    yield output_dir, ref_dir, test_dir
    _compare_outputs(output_dir, ref_dir, test_dir)


@pytest.fixture
def _record_exports(request):
    # Using the bicep recorder requires the installation of the bicep CLI:
    # https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/install#install-manually
    output_dir = _get_infra_dir()
    ref_dir = request.node.name
    yield output_dir, ref_dir, ref_dir
    validate_dir = os.path.join(output_dir, ref_dir, "*.bicep")
    args = ["bicep", "lint", "--pattern", validate_dir]
    print("Running Bicep CLI to validate the generated bicep files", args)
    output = subprocess.run(args, check=False, capture_output=True, text=True)
    linter_outputs = output.stderr.splitlines()
    for line in linter_outputs:
        error = re.search(r"Error \w+(?:-\w+)+", line)
        if error and error.group()[8:] in SUPPRESS_ERRORS:
            continue
        warning = re.search(r"Warning \w+(?:-\w+)+", line)
        if warning and warning.group()[8:] in SUPPRESS_WARNINGS:
            continue
        raise Exception("Bicep validation failed: " + line)


export_dir = _record_exports if os.environ.get("TEST_EXPORT_RECORD", "").lower() == "true" else _compare_exports
