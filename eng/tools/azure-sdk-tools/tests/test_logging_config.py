import logging
from ci_tools.logging import configure_logging, logger, run_logged
from unittest.mock import patch
import pytest
import argparse
import os


@pytest.mark.parametrize(
    "cli_args,level_env,expected_level",
    [
        (argparse.Namespace(quiet=True, verbose=False, log_level=None), "INFO", logging.ERROR),
        (argparse.Namespace(quiet=False, verbose=True, log_level=None), "INFO", logging.DEBUG),
        (argparse.Namespace(quiet=False, verbose=False, log_level="ERROR"), "INFO", logging.ERROR),
        (argparse.Namespace(quiet=False, verbose=False, log_level=None), "WARN", logging.WARNING),
    ],
)
@patch("logging.basicConfig")
def test_configure_logging_various_levels(mock_basic_config, cli_args, level_env, expected_level, monkeypatch):
    monkeypatch.setenv("LOGLEVEL", level_env)
    assert os.environ["LOGLEVEL"] == level_env
    configure_logging(cli_args)
    assert logger.level == expected_level
    mock_basic_config.assert_called_with(
        level=expected_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", force=True
    )


@pytest.mark.parametrize("stream", [True, False])
@pytest.mark.parametrize(
    "env", [None, {"SSL_CERT_FILE": "temporary.pem", "PIP_INDEX_URL": "https://example.invalid/cfs"}]
)
@patch("ci_tools.logging.subprocess.run")
def test_run_logged_passes_environment(mock_run, stream, env):
    result = run_logged(
        ["python", "-m", "cibuildwheel"], cwd="package", check=True, should_stream_to_console=stream, env=env
    )
    assert mock_run.call_args.kwargs["env"] is env
    assert mock_run.call_args.kwargs["check"] is True
    assert result is mock_run.return_value
