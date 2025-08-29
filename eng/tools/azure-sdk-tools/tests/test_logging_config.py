
import logging
from ci_tools.logging import configure_logging, logger
from unittest.mock import patch
import pytest
import argparse
import os

@pytest.mark.parametrize("cli_args,level,level_env,expected_level", [
	(argparse.Namespace(quiet=True, verbose=False, log_level=None), None, "INFO", logging.ERROR),  
	(argparse.Namespace(quiet=False, verbose=True, log_level=None), None, "INFO", logging.DEBUG),  
	(argparse.Namespace(quiet=False, verbose=False, log_level="ERROR"), "ERROR", "INFO", logging.ERROR),  
	(argparse.Namespace(quiet=False, verbose=False, log_level=None), None, "WARNING", logging.WARNING),  
    (argparse.Namespace(quiet=False, verbose=False, log_level=None), None, "DEBUG", logging.DEBUG),  
])
@patch("logging.basicConfig")
def test_configure_logging_various_levels(mock_basic_config, cli_args, level, level_env, expected_level, monkeypatch):
    monkeypatch.setenv("LOGLEVEL", level_env)
    assert os.environ["LOGLEVEL"] == level_env
    print(level_env)
    configure_logging(cli_args, level=level)
    assert logger.level == expected_level
    mock_basic_config.assert_called_with(level=expected_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
