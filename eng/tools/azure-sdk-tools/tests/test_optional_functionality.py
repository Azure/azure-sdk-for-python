import os
import pytest

from ci_tools.parsing import ParsedSetup
from ci_tools.functions import get_config_setting

integration_folder = os.path.join(os.path.dirname(__file__), "integration")


def test_toml_result():
    package_with_toml = os.path.join(integration_folder, "scenarios", "optional_environment_two_options")
    parsed_setup = ParsedSetup.from_path(package_with_toml)
    actual = parsed_setup.get_build_config()

    expected = {
        "mypy": True,
        "type_check_samples": True,
        "verifytypes": True,
        "pyright": True,
        "pylint": True,
        "black": True,
        "optional": [
            {
                "name": "no_requests",
                "install": [],
                "uninstall": ["requests"],
                "additional_pytest_args": ["-k", "*_async.py"],
            },
            {
                "name": "no_aiohttp",
                "install": [],
                "uninstall": ["aiohttp"],
                "additional_pytest_args": ["-k", "not *_async.py"],
            },
        ],
    }

    assert actual == expected


def test_optional_specific_get():
    package_with_toml = os.path.join(integration_folder, "scenarios", "optional_environment_two_options")
    actual = get_config_setting(package_with_toml, "optional")
    expected = [
        {
            "name": "no_requests",
            "install": [],
            "uninstall": ["requests"],
            "additional_pytest_args": ["-k", "*_async.py"],
        },
        {
            "name": "no_aiohttp",
            "install": [],
            "uninstall": ["aiohttp"],
            "additional_pytest_args": ["-k", "not *_async.py"],
        },
    ]

    assert expected == actual


def test_optional_specific_get_no_result():
    package_with_toml = os.path.join(integration_folder, "scenarios", "optional_environment_zero_options")
    actual = get_config_setting(package_with_toml, "optional", None)
    expected = None

    assert expected == actual
