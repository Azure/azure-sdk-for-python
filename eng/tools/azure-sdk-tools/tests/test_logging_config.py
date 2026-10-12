import logging
from ci_tools.logging import configure_logging, logger, run_logged
from unittest.mock import patch
import pytest
import argparse
import os
import sys
import subprocess


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


@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("custom_environment", [False, True])
def test_run_logged_child_environment(stream, custom_environment, tmp_path, monkeypatch, capfd):
    monkeypatch.setenv("CI_TOOLS_LOGGED_ENV_TEST", "parent")
    before = os.environ.copy()
    environment = {**before, "CI_TOOLS_LOGGED_ENV_TEST": "child"} if custom_environment else None
    result = run_logged(
        [sys.executable, "-c", "import os; print(os.environ['CI_TOOLS_LOGGED_ENV_TEST'])"],
        cwd=str(tmp_path),
        check=True,
        should_stream_to_console=stream,
        env=environment,
    )
    output = capfd.readouterr().out if stream else result.stdout
    assert output.strip() == ("child" if custom_environment else "parent")
    assert os.environ == before


@pytest.mark.parametrize("stream", [False, True])
def test_run_logged_failure_preserved(stream, tmp_path, caplog):
    with pytest.raises(subprocess.CalledProcessError) as error:
        run_logged(
            [sys.executable, "-c", "print('build failed'); raise SystemExit(7)"],
            cwd=str(tmp_path),
            check=True,
            should_stream_to_console=stream,
        )
    assert error.value.returncode == 7
    assert "Command failed:" in caplog.text
    if not stream:
        assert "build failed" in caplog.text
