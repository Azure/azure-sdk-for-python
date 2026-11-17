# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import os

from apiview_converter import convert_api_md_to_report, parse_api_md
from changelog_tracker import ChangelogTracker
from supported_checkers import CHECKERS, POST_PROCESSING_CHECKERS
from breaking_changes_allowlist import IGNORE_BREAKING_CHANGES

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
COMPUTEFLEET_API_MD = os.path.join(DATA_DIR, "computefleet_api.md")


def _changelog(stable, current):
    checker = ChangelogTracker(
        stable,
        current,
        "azure-mgmt-computefleet",
        checkers=CHECKERS,
        ignore=IGNORE_BREAKING_CHANGES,
        post_processing_checkers=POST_PROCESSING_CHECKERS,
    )
    checker.run_checks()
    return checker


def test_convert_namespaces_and_classes():
    report = convert_api_md_to_report(COMPUTEFLEET_API_MD)
    assert "azure.mgmt.computefleet" in report
    assert "azure.mgmt.computefleet.models" in report
    client = report["azure.mgmt.computefleet"]["class_nodes"]["ComputeFleetMgmtClient"]
    assert set(client["methods"]) == {"__init__", "close", "send_request"}
    assert client["properties"] == {
        "fleets": {"attr_type": "FleetsOperations"},
        "operations": {"attr_type": "Operations"},
    }
    assert client["methods"]["send_request"]["parameters"]["stream"]["param_type"] == "keyword_only"
    assert client["methods"]["send_request"]["return_type"] == "HttpResponse"


def test_convert_enum_and_model():
    models = convert_api_md_to_report(COMPUTEFLEET_API_MD)["azure.mgmt.computefleet.models"]["class_nodes"]
    enum = models["AcceleratorManufacturer"]
    assert enum["type"] == "Enum"
    assert enum["properties"] == {"AMD": "AMD", "NVIDIA": "NVIDIA", "XILINX": "XILINX"}
    model = models["AdditionalLocationsProfile"]
    assert model["type"] is None
    assert model["properties"]["location_profiles"] == {"attr_type": "list[LocationProfile]"}
    assert "__init__" not in model["methods"]


def test_self_diff_has_no_changes():
    report = convert_api_md_to_report(COMPUTEFLEET_API_MD)
    checker = _changelog(report, copy.deepcopy(report))
    assert not checker.breaking_changes
    assert not checker.features_added


def test_added_enum_member_and_removed_property():
    stable = convert_api_md_to_report(COMPUTEFLEET_API_MD)
    current = copy.deepcopy(stable)
    current["azure.mgmt.computefleet.models"]["class_nodes"]["AcceleratorManufacturer"]["properties"]["INTEL"] = "INTEL"
    del current["azure.mgmt.computefleet.models"]["class_nodes"]["AdditionalLocationsProfile"]["properties"][
        "location_profiles"
    ]
    checker = _changelog(stable, current)
    assert any("INTEL" in str(c) for c in checker.features_added)
    assert any("location_profiles" in str(c) for c in checker.breaking_changes)


def test_parse_api_md_accepts_string():
    with open(COMPUTEFLEET_API_MD, encoding="utf-8") as fd:
        report = parse_api_md(fd.read())
    assert report["azure.mgmt.computefleet.operations"]["class_nodes"]["Operations"]["methods"]["list"]
