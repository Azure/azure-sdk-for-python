# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml


TEMPLATES = Path(__file__).resolve().parents[4] / "eng" / "pipelines" / "templates" / "stages"


def load_template(name):
    return yaml.safe_load((TEMPLATES / name).read_text())


@pytest.fixture
def eligibility_step():
    stage = load_template("python-analyze-weekly.yml")["stages"][0]
    check, analyze = stage["jobs"]
    assert check["job"] == "CheckWeekend"
    assert check["variables"]["PipelineStartTime"] == "$[ format('{0:yyyyMMddHHmmssK}', pipeline.startTime) ]"
    assert check["steps"][0] == {"checkout": "none"}
    assert analyze["dependsOn"] == check["job"]
    step = check["steps"][1]
    assert step["env"]["PIPELINE_START_TIME"] == "$(PipelineStartTime)"
    assert analyze["condition"] == (
        "and(succeeded(), eq(dependencies.CheckWeekend.outputs['" + step["name"] + ".IsWeekend'], 'True'))"
    )
    return step


@pytest.mark.parametrize(
    "timestamp,expected",
    [
        ("20261012000000Z", False),
        ("20261013120000Z", False),
        ("20261014120000Z", False),
        ("20261015120000Z", False),
        ("20261016235959Z", False),
        ("20261017000000Z", True),
        ("20261018235959Z", True),
        ("20261019000000Z", False),
        ("20261016170000-07:00", True),
        ("20261019010000+02:00", True),
        ("20261018170000-07:00", False),
        ("20261017010000+02:00", False),
        ("20261016235959", False),
        ("20261017000000", True),
        ("20261018235959", True),
        ("20261019000000", False),
        ("20280229000000Z", False),
        ("20270102000000Z", True),
        ("", None),
        ("invalid", None),
    ],
)
def test_weekend_eligibility_uses_pipeline_start_time(eligibility_step, timestamp, expected):
    powershell = shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is required to execute pipeline scripts")
    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$ErrorActionPreference = 'Stop'\n" + eligibility_step["pwsh"],
        ],
        env={**os.environ, "PIPELINE_START_TIME": timestamp, "TZ": "America/Los_Angeles"},
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if expected is None:
        assert result.returncode != 0
        assert "variable=IsWeekend" not in result.stdout
    else:
        assert result.returncode == 0, result.stderr
        assert f"##vso[task.setvariable variable=IsWeekend;isOutput=true]{expected}" in result.stdout


def test_callers_preserve_scheduled_run_guards():
    archetype = load_template("archetype-sdk-tests.yml")
    packages = next(iter(archetype["extends"]["parameters"]["stages"][0].values()))
    weekly = packages[1]["${{ if eq(variables['Build.Reason'], 'Schedule') }}"][0]
    assert weekly["template"].endswith("/python-analyze-weekly.yml")
    assert weekly["parameters"]["Condition"] == "succeeded()"

    standalone = load_template("python-analyze-weekly-standalone.yml")
    weekly = standalone["extends"]["parameters"]["stages"][0]
    assert weekly["template"].endswith("/python-analyze-weekly.yml")
    assert weekly["parameters"]["Condition"] == "and(succeeded(), eq(variables['Build.Reason'], 'Schedule'))"

    for name in ("archetype-sdk-tests.yml", "python-analyze-weekly-standalone.yml", "python-analyze-weekly.yml"):
        assert "{0:ddd}" not in (TEMPLATES / name).read_text()
