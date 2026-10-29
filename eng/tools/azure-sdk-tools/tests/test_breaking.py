import argparse
import os
import sys

from unittest.mock import MagicMock, patch

from azpysdk.breaking import breaking


def _make_args(use_apistub=False, changelog=True, isolate=False):
    """Build an argparse.Namespace with every attribute breaking.run() reads."""
    return argparse.Namespace(
        target=".",
        isolate=isolate,
        command="breaking",
        service=None,
        target_module=None,
        in_venv=False,
        stable_version=None,
        changelog=changelog,
        code_report=False,
        source_report=None,
        target_report=None,
        latest_pypi_version=False,
        use_apistub=use_apistub,
        debug=False,
    )


def _run_breaking(args, tmp_path):
    """Invoke breaking.run() with all external side effects mocked out.

    Returns a dict of the mocks that assertions can inspect.
    """
    chk = breaking()
    staging = str(tmp_path / "staging")
    os.makedirs(staging, exist_ok=True)
    fake_parsed = MagicMock()
    fake_parsed.folder = str(tmp_path)
    fake_parsed.name = "azure-core"

    original_cwd = os.getcwd()
    with patch("azpysdk.breaking.set_envvar_defaults"), patch(
        "azpysdk.breaking.install_into_venv"
    ) as install_into_venv, patch("azpysdk.breaking.create_package_and_install") as create_package_and_install, patch(
        "azpysdk.breaking.check_call"
    ) as check_call, patch.object(
        chk, "get_targeted_directories", return_value=[fake_parsed]
    ), patch.object(
        chk, "get_executable", return_value=(sys.executable, staging)
    ), patch.object(
        chk, "install_dev_reqs"
    ) as install_dev_reqs:
        try:
            result = chk.run(args)
        finally:
            os.chdir(original_cwd)

    return {
        "result": result,
        "install_dev_reqs": install_dev_reqs,
        "install_into_venv": install_into_venv,
        "create_package_and_install": create_package_and_install,
        "check_call": check_call,
    }


class TestBreakingUseApistubGuard:
    """The apistub path builds the report via static analysis, so it must not install the
    package's dev requirements nor build/install the target package sdist."""

    def test_use_apistub_skips_dev_reqs_and_sdist_install(self, tmp_path):
        mocks = _run_breaking(_make_args(use_apistub=True), tmp_path)

        # The failing/expensive steps are skipped in apistub mode.
        mocks["install_dev_reqs"].assert_not_called()
        mocks["create_package_and_install"].assert_not_called()

        # jsondiff + breaking-change checker are still required by the detector.
        mocks["install_into_venv"].assert_called_once()

        # The detector still runs, and it receives --use-apistub.
        mocks["check_call"].assert_called_once()
        detector_cmd = mocks["check_call"].call_args.args[0]
        assert "--use-apistub" in detector_cmd
        assert mocks["result"] == 0

    def test_default_path_installs_dev_reqs_and_sdist(self, tmp_path):
        mocks = _run_breaking(_make_args(use_apistub=False), tmp_path)

        # The import-based path needs the package (and its deps) installed.
        mocks["install_dev_reqs"].assert_called_once()
        mocks["create_package_and_install"].assert_called_once()

        mocks["install_into_venv"].assert_called_once()

        mocks["check_call"].assert_called_once()
        detector_cmd = mocks["check_call"].call_args.args[0]
        assert "--use-apistub" not in detector_cmd
        assert mocks["result"] == 0
