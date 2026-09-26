# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest.mock import patch

from azpysdk.main import build_parser
from azpysdk.whl import whl


def test_disablecov_is_accepted_before_test_command():
    args = build_parser().parse_args(["--disablecov", "whl", "package"])

    assert args.disablecov


def test_whl_pytest_args_enable_package_coverage():
    check = whl()
    args = SimpleNamespace(
        command="whl",
        disablecov=False,
        mark_arg=None,
        pytest_args=None,
    )

    with patch(
        "azpysdk.install_and_test.ParsedSetup.from_path",
        return_value=SimpleNamespace(namespace="azure.storage.blob"),
    ):
        pytest_args = check._build_pytest_args("package", args)

    assert "--cov=azure.storage.blob" in pytest_args
    assert check.get_coverage_file("package").endswith(".coverage.whl")


def test_whl_pytest_args_disable_package_coverage():
    check = whl()
    args = SimpleNamespace(
        command="whl",
        disablecov=True,
        mark_arg=None,
        pytest_args=None,
    )

    with patch("azpysdk.install_and_test.ParsedSetup.from_path") as parsed_setup:
        pytest_args = check._build_pytest_args("package", args)

    assert not any(arg.startswith("--cov=") for arg in pytest_args)
    parsed_setup.assert_not_called()
