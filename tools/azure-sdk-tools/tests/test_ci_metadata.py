import os, tempfile, shutil

import pytest

from ci_tools.parsing import get_ci_config
from ci_tools.environment_exclusions import is_check_enabled

integration_folder = os.path.join(os.path.dirname(__file__), "integration")
scenario_present = os.path.join(integration_folder, "scenarios", "ci_yml_present", "service", "fake-package")
scenario_not_present = os.path.join(integration_folder, "scenarios", "ci_yml_not_present", "service", "fake-package")

def test_ci_config_present():
    config = get_ci_config(scenario_present)
    assert config is not None
    assert type(config) is dict
    assert type(config["extends"]) is dict

    should_proxy = config.get("extends", {}).get("parameters", {}).get("TestProxy", True)
    assert should_proxy == False

def test_ci_config_non_present():
    config = get_ci_config(scenario_not_present)
    assert config is None