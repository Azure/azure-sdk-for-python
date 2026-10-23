import os
import pytest
import json
from unittest.mock import Mock

import yaml

from ci_tools.conda.CondaConfiguration import CondaConfiguration
from ci_tools.conda import conda_functions


def test_conda_config_retrieve():
    raw_json = """
    {
        "name": "azure-core",
        "common_root": "azure",
        "service": "core",
        "in_batch": true,
        "checkout": [
            {
                "package": "azure-core",
                "version": "1.32.0"
            },
            {
                "package": "azure-mgmt-core",
                "version": "1.5.0"
            },
            {
                "package": "azure-common",
                "version": "1.1.28"
            }
        ]
    }
    """

    CondaConfiguration.from_json(json.loads(raw_json))


def test_conda_host_environment_uses_python_311():
    environment = yaml.safe_load(conda_functions.CONDA_ENV_FILE)
    assert "python=3.11" in environment["dependencies"]


@pytest.mark.parametrize("version", [None, "3.11", "311", "3.12", "312", "3.14", "3.11.9"])
def test_conda_build_explicitly_selects_supported_python(version, monkeypatch):
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(conda_functions.subprocess, "run", run)
    assert conda_functions.invoke_conda_build("output", "env", "recipe", version, ["extra-channel"]) == 0
    command = run.call_args.args[0]
    assert command[:5] == ["conda", "run", "--prefix", "env", "conda-build"]
    assert command[-2:] == ["--py", version or "3.11"]
    assert ["-c", "extra-channel"] == command[-4:-2]
    assert run.call_args.kwargs == {"cwd": "recipe", "check": False}


@pytest.mark.parametrize("version", ["3.9", "39", "3.10", "310", "2.7", "3.11rc1", "invalid"])
def test_conda_build_rejects_older_or_invalid_python_before_running(version, monkeypatch):
    run = Mock()
    monkeypatch.setattr(conda_functions.subprocess, "run", run)
    with pytest.raises(ValueError, match="require Python 3.11"):
        conda_functions.invoke_conda_build("output", "env", "recipe", version)
    run.assert_not_called()
