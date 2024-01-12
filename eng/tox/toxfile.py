import os
from logging import getLogger
from pathlib import Path

from tox import plugin
from tox.config.sets import CoreConfigSet
from tox.session.state import State

logger = getLogger(__file__)

NAME = "azure-sdk-for-python tox plugin"

@plugin.impl
def tox_add_core_config(core_conf: CoreConfigSet, state: State):
    core_conf.add_constant(
        "repository_root",
        "The root of this git repository",
        next(p for p in Path(core_conf["config_file_path"]).resolve().parents if (p / ".git").exists()),
    )

    core_conf.add_constant(
        "pytest_log_level",
        "The log level to use for pytest, supplied as environment or queue time variable PYTEST_LOG_LEVEL",
        os.getenv("PYTEST_LOG_LEVEL", "51")  # Defaults to no logging
    )
