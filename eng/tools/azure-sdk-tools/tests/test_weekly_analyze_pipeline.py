# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
import yaml


TEMPLATES = Path(__file__).resolve().parents[4] / "eng" / "pipelines" / "templates" / "stages"


def load_template(name):
    return yaml.safe_load((TEMPLATES / name).read_text())


@pytest.fixture
def eligibility_job():
    return load_template("python-analyze-weekly.yml")["stages"][0]["jobs"][0]


@pytest.fixture
def eligibility_step():
    template = load_template("python-analyze-weekly.yml")
    condition = next(parameter for parameter in template["parameters"] if parameter["name"] == "Condition")
    assert condition["default"] == "succeeded()"
    stage = template["stages"][0]
    check, analyze = stage["jobs"]
    assert check["job"] == "CheckWeekend"
    assert stage["condition"] == "${{ parameters.Condition }}"
    assert check["steps"][0] == {"checkout": "none"}
    assert analyze["dependsOn"] == check["job"]
    step = check["steps"][1]
    assert step["env"]["PIPELINE_START_TIME"] == "$(PipelineStartTime)"
    assert analyze["condition"] == (
        "and(succeeded(), eq(dependencies.CheckWeekend.outputs['" + step["name"] + ".IsWeekend'], 'True'))"
    )
    return step


@pytest.fixture
def format_start_time(eligibility_job):
    expression = eligibility_job["variables"]["PipelineStartTime"]
    match = re.fullmatch(r"\$\[ format\('\{0:([^}]+)\}', pipeline\.startTime\) \]", expression)
    assert match, expression
    specifier = match[1]
    # Azure's documented specifiers are a subset of .NET's, not arbitrary .ToString() formats:
    # https://learn.microsoft.com/azure/devops/pipelines/process/expressions#format
    tokens = re.findall(r"yyyy|MM|dd|HH|mm|ss|K", specifier)
    assert "".join(tokens) == specifier, f"Unsupported pipeline date format: {specifier}"

    def format_timestamp(timestamp):
        start = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        values = {
            "yyyy": f"{start.year:04d}",
            "MM": f"{start.month:02d}",
            "dd": f"{start.day:02d}",
            "HH": f"{start.hour:02d}",
            "mm": f"{start.minute:02d}",
            "ss": f"{start.second:02d}",
            "K": timestamp[19:],
        }
        return "".join(values[token] for token in tokens)

    return format_timestamp


@pytest.mark.parametrize(
    "timestamp,expected",
    [
        ("2026-10-17T00:00:00Z", "20261017000000Z"),
        ("2026-10-17T00:00:00+00:00", "20261017000000+00:00"),
        ("2026-10-16T17:00:00-07:00", "20261016170000-07:00"),
        ("2026-10-17T02:00:00+02:00", "20261017020000+02:00"),
        ("2026-10-17T00:00:00", "20261017000000"),
    ],
)
def test_pipeline_start_time_uses_supported_format(format_start_time, timestamp, expected):
    assert format_start_time(timestamp) == expected


def test_timezone_free_pipeline_timestamps_are_explicitly_utc(eligibility_step):
    # Behavioral cases alone cannot detect a local-time default on an agent already in UTC.
    assert "[Globalization.DateTimeStyles]::AssumeUniversal" in eligibility_step["pwsh"]


def run_eligibility(step, timestamp, **environment):
    powershell = shutil.which("pwsh")
    if not powershell:
        pytest.skip("PowerShell is required to execute pipeline scripts")
    env = {**os.environ, **environment}
    env.pop("PIPELINE_START_TIME", None)
    if timestamp is not None:
        env["PIPELINE_START_TIME"] = timestamp
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            "$ErrorActionPreference = 'Stop'\n"
            "function Get-Date { throw 'Eligibility must use the pipeline start time' }\n" + step["pwsh"],
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.mark.parametrize(
    "timestamp,expected",
    [
        ("2026-10-12T00:00:00Z", False),
        ("2026-10-13T12:00:00Z", False),
        ("2026-10-14T12:00:00Z", False),
        ("2026-10-15T12:00:00Z", False),
        ("2026-10-16T23:59:59Z", False),
        ("2026-10-17T00:00:00Z", True),
        ("2026-10-17T23:59:59Z", True),
        ("2026-10-18T00:00:00Z", True),
        ("2026-10-18T23:59:59Z", True),
        ("2026-10-19T00:00:00Z", False),
        ("2026-10-16T17:00:00-07:00", True),
        ("2026-10-19T01:00:00+02:00", True),
        ("2026-10-18T17:00:00-07:00", False),
        ("2026-10-17T01:00:00+02:00", False),
        ("2026-10-17T00:00:00+00:00", True),
        ("2026-10-16T12:00:00-12:00", True),
        ("2026-10-19T13:59:59+14:00", True),
        ("2026-10-19T14:00:00+14:00", False),
        ("2020-02-28T23:59:59Z", False),
        ("2020-02-29T00:00:00Z", True),
        ("2020-03-01T23:59:59Z", True),
        ("2020-03-02T00:00:00Z", False),
        ("2028-02-29T00:00:00Z", False),
        ("2028-03-01T00:00:00Z", False),
        ("2026-01-31T23:59:59Z", True),
        ("2026-02-01T00:00:00Z", True),
        ("2026-02-02T00:00:00Z", False),
        ("2026-12-31T23:59:59Z", False),
        ("2027-01-01T00:00:00Z", False),
        ("2027-01-02T00:00:00Z", True),
        ("2022-12-31T23:59:59Z", True),
        ("2023-01-01T00:00:00Z", True),
        ("2023-01-02T00:00:00Z", False),
        ("2026-10-16T23:59:59", False),
        ("2026-10-17T00:00:00", True),
        ("2026-10-18T23:59:59", True),
        ("2026-10-19T00:00:00", False),
    ],
)
def test_weekend_eligibility_uses_pipeline_start_time(eligibility_step, format_start_time, timestamp, expected):
    result = run_eligibility(eligibility_step, format_start_time(timestamp), TZ="Pacific/Honolulu")
    assert result.returncode == 0, result.stderr
    assert f"##vso[task.setvariable variable=IsWeekend;isOutput=true]{expected}" in result.stdout


@pytest.mark.parametrize(
    "timestamp", [None, "", "invalid", "$(PipelineStartTime)", "20260230000000Z", "20261017240000Z"]
)
def test_invalid_pipeline_start_time_fails_closed(eligibility_step, timestamp):
    result = run_eligibility(eligibility_step, timestamp)
    assert result.returncode != 0
    assert "variable=IsWeekend" not in result.stdout


@pytest.mark.parametrize("timestamp,expected", [("2026-10-17T00:00:00Z", True), ("2026-10-19T00:00:00Z", False)])
def test_job_retry_preserves_original_start_day(eligibility_step, format_start_time, timestamp, expected):
    outputs = []
    for attempt in ("1", "2"):
        result = run_eligibility(eligibility_step, format_start_time(timestamp), SYSTEM_JOBATTEMPT=attempt)
        assert result.returncode == 0, result.stderr
        output = f"##vso[task.setvariable variable=IsWeekend;isOutput=true]{expected}"
        assert output in result.stdout
        outputs.append(result.stdout)
    assert outputs[0] == outputs[1]


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
